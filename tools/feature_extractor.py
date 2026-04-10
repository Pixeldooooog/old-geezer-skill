#!/usr/bin/env python3
"""
老登语料特征提取器

从 source_parser.py 的 JSON 输出中自动提取说话特征：
- 语气词频率、口头禅候选
- 打断/说教/不懂装懂等行为标记频率
- 反问比例、句子长度分布、起手/收尾模式
- 话题分段和行为模式聚类
- 自动计算 8 维权重
- 自动检测最匹配的原型组合
"""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path


def load_markers(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def compute_speaker_stats(utterances: list[dict], target_speaker: str | None = None) -> dict:
    """每人的基本统计"""
    from collections import defaultdict
    by_speaker = defaultdict(list)
    for u in utterances:
        by_speaker[u.get("speaker", "unknown")].append(u)

    stats = {}
    total_chars = sum(len(u["content"]) for u in utterances) or 1
    total_utterances = len(utterances) or 1

    for speaker, utts in by_speaker.items():
        chars = [len(u["content"]) for u in utts]
        chars_sorted = sorted(chars)
        n = len(chars)
        median = chars_sorted[n // 2] if n > 0 else 0

        timestamps = [u.get("timestamp", "") for u in utts if u.get("timestamp")]
        stats[speaker] = {
            "utterance_count": n,
            "total_chars": sum(chars),
            "avg_length": round(sum(chars) / n, 1) if n else 0,
            "median_length": median,
            "max_length": max(chars) if chars else 0,
            "share_pct": round(sum(chars) / total_chars * 100, 1),
            "utterance_share_pct": round(n / total_utterances * 100, 1),
        }

    if target_speaker and target_speaker in stats:
        stats["_target"] = target_speaker

    return stats


def compute_lexical_features(utterances: list[dict], target_speaker: str, markers: dict) -> dict:
    """词汇级别特征：填充词、重复模式、口头禅候选"""
    target_utts = [u for u in utterances if u.get("speaker") == target_speaker]
    if not target_utts:
        target_utts = utterances

    all_text = " ".join(u["content"] for u in target_utts)
    total_chars = len(all_text) or 1
    total_kchars = total_chars / 1000

    # 填充词
    filler_words = markers.get("filler_words", {})
    filler_counts = {}
    for word in filler_words:
        count = all_text.count(word)
        if count > 0:
            filler_counts[word] = {
                "count": count,
                "per_1k": round(count / total_kchars, 2),
            }
    filler_total = sum(f["count"] for f in filler_counts.values())

    # 重复模式
    repetition_patterns = markers.get("repetition_patterns", {})
    repetition_counts = {}
    for pattern, cfg in repetition_patterns.items():
        count = all_text.count(pattern)
        if count > 0:
            repetition_counts[pattern] = {
                "count": count,
                "per_1k": round(count / total_kchars, 2),
            }

    # n-gram 口头禅候选 (3-8 chars, >= 3 occurrences, 必须含中文)
    stop_words = set(markers.get("stop_words", []))
    has_chinese = re.compile(r'[\u4e00-\u9fff]')

    # 通用片段黑名单：这些太短/太通用，不可能是口头禅
    generic_fragments = {
        "些东西", "个东西", "种情况", "个东西", "种东西", "些事情", "个事情",
        "那个什", "个什么", "些什么", "些什么", "怎么说", "什么意思",
        "一个那", "一个这", "这个那", "这个什",
    }

    ngram_counts = Counter()
    for n in range(3, 9):
        for text in [u["content"] for u in target_utts]:
            # 清理：去掉标点和多余空格
            cleaned = re.sub(r'[，。！？、；：""''（）\s]', '', text)
            for i in range(len(cleaned) - n + 1):
                gram = cleaned[i:i + n]
                # 必须包含至少一个中文字符
                if not has_chinese.search(gram):
                    continue
                if any(w in gram for w in stop_words):
                    continue
                if gram in stop_words:
                    continue
                if gram in generic_fragments:
                    continue
                # 过滤全是虚词的组合：要求至少有一个"实质词"（2字以上的名词性片段）
                ngram_counts[gram] += 1

    # 过滤：至少出现 3 次，且在多个 utterance 中出现
    # 额外：计算 speaker 特异性（只在该 speaker 中高频才算口头禅）
    all_speaker_utts = [u["content"] for u in utterances if u.get("speaker") != target_speaker]
    other_text = " ".join(all_speaker_utts) if all_speaker_utts else ""
    other_kchars = len(other_text) / 1000 or 1

    catchphrase_candidates = []
    utt_texts = [u["content"] for u in target_utts]
    for gram, count in ngram_counts.most_common(80):
        if count < 3:
            break
        # 检查在多少个 utterance 中出现
        spread = sum(1 for t in utt_texts if gram in t)
        if spread >= 2:
            # 计算 speaker 特异性：该词在目标 speaker 中的频率 vs 其他人的频率
            target_freq = count / total_kchars
            other_count = other_text.count(gram) if other_text else 0
            other_freq = other_count / other_kchars
            specificity = round(target_freq / (other_freq + 0.01), 2)  # 越高越独特

            catchphrase_candidates.append({
                "phrase": gram,
                "count": count,
                "spread": spread,
                "per_1k": round(count / total_kchars, 2),
                "specificity": specificity,
            })

    # 按 specificity 排序，特异性高的排在前面
    catchphrase_candidates.sort(key=lambda x: x["specificity"], reverse=True)
    catchphrase_candidates = catchphrase_candidates[:20]

    return {
        "total_chars": total_chars,
        "filler_words": filler_counts,
        "filler_total_per_1k": round(filler_total / total_kchars, 2),
        "repetition_patterns": repetition_counts,
        "catchphrase_candidates": catchphrase_candidates[:20],
    }


def compute_structural_features(utterances: list[dict], target_speaker: str) -> dict:
    """句子级别特征：反问比例、长度分布、起手/收尾"""
    target_utts = [u for u in utterances if u.get("speaker") == target_speaker]
    if not target_utts:
        target_utts = utterances

    total = len(target_utts) or 1

    # 反问比例
    question_suffixes = ["吗", "吧", "呢", "？", "?"]
    question_count = 0
    for u in target_utts:
        content = u["content"].strip()
        if not content:
            continue
        if content[-1] in question_suffixes:
            question_count += 1
        elif any(s in content for s in ["对吧", "好吗", "明白吗", "是吧", "懂吗"]):
            question_count += 1

    question_ratio = round(question_count / total, 3)

    # 句子长度分布
    lengths = [len(u["content"]) for u in target_utts]
    buckets = {"short": 0, "medium": 0, "long": 0, "very_long": 0}
    for l in lengths:
        if l < 20:
            buckets["short"] += 1
        elif l < 80:
            buckets["medium"] += 1
        elif l < 200:
            buckets["long"] += 1
        else:
            buckets["very_long"] += 1
    for k in buckets:
        buckets[k] = round(buckets[k] / total, 3)

    # 起手模式 top20 (前 1-4 字)
    starters = Counter()
    for u in target_utts:
        content = u["content"].strip()
        if not content:
            continue
        for n in range(2, 5):
            prefix = content[:n]
            if len(prefix) == n:
                starters[prefix] += 1

    # 收尾模式 top20 (后 1-4 字)
    enders = Counter()
    for u in target_utts:
        content = u["content"].strip()
        if not content:
            continue
        for n in range(1, 5):
            suffix = content[-n:]
            if len(suffix) == n:
                enders[suffix] += 1

    return {
        "question_count": question_count,
        "question_ratio": question_ratio,
        "length_distribution": buckets,
        "top_starters": [{"prefix": s, "count": c} for s, c in starters.most_common(20)],
        "top_enders": [{"suffix": s, "count": c} for s, c in enders.most_common(20)],
    }


def compute_behavioral_markers(utterances: list[dict], target_speaker: str, markers: dict) -> dict:
    """8 个维度的行为标记计数"""
    target_utts = [u for u in utterances if u.get("speaker") == target_speaker]
    if not target_utts:
        target_utts = utterances

    all_text = " ".join(u["content"] for u in target_utts)
    total_kchars = len(all_text) / 1000 or 1

    dimensions = markers.get("dimensions", {})
    results = {}

    for dim_name, dim_cfg in dimensions.items():
        strong_signals = dim_cfg.get("strong_signals", dim_cfg.get("markers", []))
        weak_signals = dim_cfg.get("weak_signals", [])
        legacy_markers = dim_cfg.get("markers", [])
        contextual_rules = dim_cfg.get("contextual_rules", [])

        total_count = 0
        weighted_count = 0.0
        marker_detail = {}
        strong_hits = {}
        weak_hits = {}
        contextual_matches = []

        for signal in strong_signals:
            c = all_text.count(signal)
            if c > 0:
                strong_hits[signal] = c
                marker_detail[signal] = c
                total_count += c
                weighted_count += c

        for signal in weak_signals:
            c = all_text.count(signal)
            if c > 0:
                weak_hits[signal] = c
                marker_detail[signal] = c
                total_count += c
                weighted_count += c * 0.35

        # backward compatibility for configs that still only define `markers`
        for signal in legacy_markers:
            if signal in strong_hits or signal in weak_hits:
                continue
            c = all_text.count(signal)
            if c > 0:
                marker_detail[signal] = c
                total_count += c
                weighted_count += c

        for rule in contextual_rules:
            all_of = rule.get("all_of", [])
            any_of = rule.get("any_of", [])
            if all(all_signal in all_text for all_signal in all_of) and (
                not any_of or any(any_signal in all_text for any_signal in any_of)
            ):
                contextual_matches.append(
                    {
                        "name": rule.get("name", "context_rule"),
                        "weight": rule.get("weight", 1.0),
                        "all_of": all_of,
                        "any_of": any_of,
                    }
                )
                weighted_count += rule.get("weight", 1.0)

        results[dim_name] = {
            "total_count": total_count,
            "weighted_count": round(weighted_count, 2),
            "per_1k": round(weighted_count / total_kchars, 2),
            "detail": marker_detail,
            "strong_signal_hits": strong_hits,
            "weak_signal_hits": weak_hits,
            "contextual_matches": contextual_matches,
            "description": dim_cfg.get("description", ""),
        }

    return results


def compute_auto_weights(behavioral_markers: dict, structural_features: dict, lexical_features: dict, markers: dict) -> dict:
    """从标记频率自动计算 1-5 权重"""
    thresholds = markers.get("weight_thresholds", {})
    weights = {}

    for dim_name, data in behavioral_markers.items():
        per_1k = data.get("per_1k", 0)
        dim_thresholds = thresholds.get(dim_name, {})
        score = 1
        for level in ["2", "3", "4", "5"]:
            if per_1k >= dim_thresholds.get(level, 999):
                score = int(level)
        weights[dim_name] = score

    # tone_density 用填充词总密度
    filler_density = lexical_features.get("filler_total_per_1k", 0)
    tone_thresholds = thresholds.get("tone_density", {})
    tone_score = 1
    for level in ["2", "3", "4", "5"]:
        if filler_density >= tone_thresholds.get(level, 999):
            tone_score = int(level)
    weights["tone_density"] = tone_score

    # questioning 额外参考反问比例
    q_ratio = structural_features.get("question_ratio", 0)
    q_per_1k = behavioral_markers.get("questioning", {}).get("per_1k", 0)
    combined_q = q_per_1k * 0.5 + q_ratio * 10  # 加权组合
    q_thresholds = thresholds.get("questioning", {})
    q_score = 1
    for level in ["2", "3", "4", "5"]:
        if combined_q >= q_thresholds.get(level, 999):
            q_score = int(level)
    weights["questioning"] = max(weights.get("questioning", 1), q_score)

    return weights


def detect_archetype(weights: dict, utterances: list[dict], target_speaker: str, markers: dict) -> dict:
    """通过余弦相似度 + 关键词匹配检测最匹配的原型"""
    profiles = markers.get("archetype_profiles", {})
    target_utts = [u for u in utterances if u.get("speaker") == target_speaker]
    all_text = " ".join(u["content"] for u in target_utts).lower() if target_utts else ""

    weight_vector = []
    dim_order = list(profiles.get("workplace", {}).get("canonical_weights", {}).keys())
    for dim in dim_order:
        weight_vector.append(weights.get(dim, 1))

    def cosine_sim(a: list, b: list) -> float:
        dot = sum(x * y for x, y in zip(a, b))
        mag_a = math.sqrt(sum(x * x for x in a)) or 1
        mag_b = math.sqrt(sum(x * x for x in b)) or 1
        return dot / (mag_a * mag_b)

    results = []
    for arch_name, arch_cfg in profiles.items():
        canonical = [arch_cfg["canonical_weights"].get(d, 1) for d in dim_order]
        similarity = cosine_sim(weight_vector, canonical)

        # 关键词匹配加分
        keywords = arch_cfg.get("keywords", [])
        keyword_hits = sum(1 for kw in keywords if kw.lower() in all_text)
        keyword_bonus = min(keyword_hits * 0.05, 0.2)
        confidence = min(similarity + keyword_bonus, 1.0)

        results.append({
            "type": arch_name,
            "similarity": round(similarity, 3),
            "keyword_hits": keyword_hits,
            "confidence": round(confidence, 3),
        })

    results.sort(key=lambda x: x["confidence"], reverse=True)

    primary = results[0] if results else {"type": "workplace", "confidence": 0}
    secondary = results[1] if len(results) > 1 else {"type": "internet", "confidence": 0}

    # 计算 mix_ratio
    total_conf = primary["confidence"] + secondary["confidence"] or 1
    primary_pct = round(primary["confidence"] / total_conf * 100)
    secondary_pct = 100 - primary_pct

    return {
        "primary": {"type": primary["type"], "confidence": primary["confidence"]},
        "secondary": {"type": secondary["type"], "confidence": secondary["confidence"]},
        "mix_ratio": f"{primary_pct}/{secondary_pct}",
        "all_rankings": results,
    }


def segment_episodes(utterances: list[dict], target_speaker: str, gap_seconds: int = 60) -> list[dict]:
    """按时间间隔分段，分析每段行为模式"""
    from collections import defaultdict

    if not utterances:
        return []

    # 提取可解析时间戳的 utterance
    timed_utts = []
    for u in utterances:
        ts = u.get("timestamp", "")
        if ts:
            try:
                # 尝试解析常见格式
                for fmt in ["%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y/%m/%d %H:%M:%S"]:
                    try:
                        dt = datetime.strptime(ts.strip(), fmt)
                        timed_utts.append({**u, "_datetime": dt})
                        break
                    except ValueError:
                        continue
            except Exception:
                pass

    if len(timed_utts) < 3:
        # 无法分段，返回单段
        return [_analyze_segment(utterances, target_speaker, 0)]

    # 按时间间隔分段
    segments = []
    current_segment = [timed_utts[0]]

    for i in range(1, len(timed_utts)):
        gap = (timed_utts[i]["_datetime"] - timed_utts[i - 1]["_datetime"]).total_seconds()
        if gap > gap_seconds:
            segments.append(current_segment)
            current_segment = [timed_utts[i]]
        else:
            current_segment.append(timed_utts[i])
    segments.append(current_segment)

    # 分析每段（跳过目标 speaker 没发言的段）
    episodes = []
    ep_idx = 0
    for seg in segments:
        target_in_seg = [u for u in seg if u.get("speaker") == target_speaker]
        if not target_in_seg:
            continue
        ep = _analyze_segment(seg, target_speaker, ep_idx)
        episodes.append(ep)
        ep_idx += 1

    # 简单聚类：按行为指标分 2-4 个模式
    if len(episodes) >= 2:
        _cluster_episodes(episodes)

    return episodes


def _analyze_segment(utterances: list[dict], target_speaker: str, index: int) -> dict:
    """分析一个片段的行为指标"""
    target_utts = [u for u in utterances if u.get("speaker") == target_speaker]
    all_target_text = " ".join(u["content"] for u in target_utts)
    n = len(target_utts) or 1
    total_kchars = len(all_target_text) / 1000 or 1

    # 简单关键词提取（取高频非停用词）
    words = re.findall(r'[\u4e00-\u9fff]{2,}', all_target_text)
    word_counts = Counter(words)
    top_words = [w for w, c in word_counts.most_common(10)]

    # 反问比例
    q_count = sum(1 for u in target_utts if u["content"].strip() and u["content"].strip()[-1] in "吗吧呢？?")
    q_ratio = round(q_count / n, 3)

    # 平均长度
    avg_len = round(sum(len(u["content"]) for u in target_utts) / n, 1)

    # 简单标记计数
    interruption_markers = ["等一下", "不是不是", "我说个事儿", "我来解释", "我来说", "我问一下"]
    int_count = sum(all_target_text.count(m) for m in interruption_markers)
    int_per_1k = round(int_count / total_kchars, 2)

    # 填充词密度
    fillers = ["啊", "呃", "嗯", "那个", "就是说", "这个"]
    filler_count = sum(all_target_text.count(f) for f in fillers)
    filler_per_1k = round(filler_count / total_kchars, 2)

    trigger_signals = _infer_trigger_signals(utterances, target_speaker, all_target_text)
    scene_label = _label_scene_mode(trigger_signals)
    behavior_chain = _infer_behavior_chain(all_target_text)

    return {
        "index": index,
        "utterance_count": len(target_utts),
        "total_chars": len(all_target_text),
        "avg_utterance_length": avg_len,
        "question_ratio": q_ratio,
        "interruption_markers_per_1k": int_per_1k,
        "filler_density": filler_per_1k,
        "top_keywords": top_words[:5],
        "trigger_signals": trigger_signals,
        "scene_label": scene_label,
        "behavior_chain": behavior_chain,
        "behavior_label": "",
    }


def _infer_trigger_signals(segment_utts: list[dict], target_speaker: str, target_text: str) -> list[str]:
    segment_text = " ".join(u["content"] for u in segment_utts)
    signals = []

    if any(token in target_text for token in ["你先别说", "等一下", "方向不对", "我先把结论"]):
        signals.append("challenge")
    elif any(token in segment_text for token in ["可是", "但是", "不一定"]):
        signals.append("challenge")

    if any(token in target_text for token in ["我年轻的时候", "当年", "以前", "我们那会儿"]):
        signals.append("glory_days")

    if any(token in target_text for token in ["谁负责", "什么时候交付", "我关心的是", "结论"]):
        signals.append("authority")

    if any(token in target_text for token in ["我跟你说", "先说清楚", "问题是", "首先"]):
        signals.append("lecturing")

    return signals


def _label_scene_mode(trigger_signals: list[str]) -> str:
    signal_set = set(trigger_signals)
    if "glory_days" in signal_set and "authority" in signal_set:
        return "资历施压"
    if "challenge" in signal_set and ("authority" in signal_set or "lecturing" in signal_set):
        return "控场定调"
    if "lecturing" in signal_set:
        return "展开说教"
    if "authority" in signal_set:
        return "裁判发令"
    return "混合型"


def _infer_behavior_chain(text: str) -> list[str]:
    chain = []

    if any(token in text for token in ["等一下", "你先别说", "慢着"]):
        chain.append("打断截流")
    if any(token in text for token in ["方向不对", "不成立", "不行", "有问题"]):
        chain.append("直接定性")
    if any(token in text for token in ["我先把结论", "说白了", "本质上", "我觉得"]):
        chain.append("结论先行")
    if any(token in text for token in ["谁负责", "owner", "什么时候交付", "时间节点"]):
        chain.append("责任追问")
    if any(token in text for token in ["我年轻的时候", "当年", "以前"]):
        chain.append("搬出资历")
    if any(token in text for token in ["关键是", "底层逻辑", "格局", "终局"]):
        chain.append("拉高抽象")

    return chain or ["平铺表达"]


def _cluster_episodes(episodes: list[dict]) -> None:
    """简单 K-means 聚类（K=2-4），给每个 episode 打标签"""
    if len(episodes) < 2:
        return

    # 特征向量：[avg_length, question_ratio, interruption_per_1k, filler_density]
    features = []
    for ep in episodes:
        features.append([
            ep["avg_utterance_length"] / 200,  # 归一化
            ep["question_ratio"] / 0.5,
            ep["interruption_markers_per_1k"] / 5,
            ep["filler_density"] / 50,
        ])

    n = len(features)
    k = min(3, n)

    # 简单聚类：按 avg_length 和 interruption 分
    # 高长度+高打断 = 主动追问型
    # 高问句+低长度 = 盘问型
    # 高填充+中长度 = 说教型
    # 低一切 = 被动回应型

    for i, ep in enumerate(episodes):
        f = features[i]
        avg_len = f[0]
        q_ratio = f[1]
        inter = f[2]
        filler = f[3]

        if avg_len > 0.5 and inter > 0.3:
            ep["behavior_label"] = "主动输出型"
        elif q_ratio > 0.5 and inter > 0.2:
            ep["behavior_label"] = "追问施压型"
        elif filler > 0.3 and avg_len > 0.3:
            ep["behavior_label"] = "说教展开型"
        elif avg_len < 0.2:
            ep["behavior_label"] = "被动回应型"
        else:
            ep["behavior_label"] = "混合型"


def compare_speakers(utterances: list[dict], markers: dict) -> list[dict]:
    """对比所有发言人的特征，按"老登指数"排名"""
    from collections import defaultdict
    by_speaker = defaultdict(list)
    for u in utterances:
        by_speaker[u.get("speaker", "unknown")].append(u)

    speaker_profiles = {}
    for speaker, utts in by_speaker.items():
        if len(utts) < 3:  # 太少的不分析
            continue
        lexical = compute_lexical_features(utterances, speaker, markers)
        structural = compute_structural_features(utterances, speaker)
        behavioral = compute_behavioral_markers(utterances, speaker, markers)
        weights = compute_auto_weights(behavioral, structural, lexical, markers)

        # 老登指数 = 加权总分
        # 核心维度权重更高
        geezer_score = (
            weights.get("interruption", 1) * 1.5 +
            weights.get("lecturing", 1) * 1.5 +
            weights.get("bluffing", 1) * 1.0 +
            weights.get("questioning", 1) * 1.2 +
            weights.get("tone_density", 1) * 0.8 +
            weights.get("profanity", 1) * 0.5 +
            weights.get("name_dropping", 1) * 0.8 +
            weights.get("glory_days", 1) * 1.0
        )

        speaker_profiles[speaker] = {
            "utterance_count": len(utts),
            "weights": weights,
            "geezer_score": round(geezer_score, 2),
            "top_fillers": list(lexical.get("filler_words", {}).keys())[:3],
            "question_ratio": structural.get("question_ratio", 0),
            "avg_length": round(sum(len(u["content"]) for u in utts) / len(utts), 1),
        }

    # 按老登指数排序
    ranking = sorted(speaker_profiles.items(), key=lambda x: -x[1]["geezer_score"])

    result = []
    for rank, (speaker, profile) in enumerate(ranking, 1):
        result.append({
            "rank": rank,
            "speaker": speaker,
            **profile,
        })

    return result


def compute_cognitive_proxies(utterances: list[dict], target_speaker: str) -> dict:
    """计算认知模式的可量化代理指标"""
    target_utts = [u for u in utterances if u.get("speaker") == target_speaker]
    if not target_utts:
        return {}

    all_text = " ".join(u["content"] for u in target_utts)
    n = len(target_utts) or 1
    total_kchars = len(all_text) / 1000 or 1

    # 1. 结论先行率：先抛结论再给理由的 utterance 占比
    # 检测模式：句子以判断/评价开头，后面跟"因为""所以""因为"
    conclusion_first_patterns = [
        r'^(我觉得|我认为|这个首先|这个就是|说白了|本质上|这个完全)',
    ]
    conclusion_first_count = 0
    for u in target_utts:
        content = u["content"].strip()
        for pat in conclusion_first_patterns:
            if re.match(pat, content):
                conclusion_first_count += 1
                break
    conclusion_first_rate = round(conclusion_first_count / n, 3)

    # 2. 类比频率：用类比/过去经验论证的 utterance 占比
    analogy_patterns = ["以前", "当年", "那时候", "我们以前", "就像", "像我们", "跟XX一样", "类似"]
    analogy_count = sum(1 for u in target_utts if any(p in u["content"] for p in analogy_patterns))
    analogy_rate = round(analogy_count / n, 3)
    analogy_per_1k = round(analogy_count / total_kchars, 2)

    # 3. 战略拉高频率：从细节跳到高层论述
    strategic_patterns = ["终局", "本质", "底层逻辑", "核心问题", "关键是", "根本上是", "博弈", "格局"]
    strategic_count = sum(1 for u in target_utts if any(p in u["content"] for p in strategic_patterns))
    strategic_rate = round(strategic_count / n, 3)
    strategic_per_1k = round(strategic_count / total_kchars, 2)

    # 4. 降维回避率：回避细节的行为
    deflect_patterns = ["这个你们定", "这个先不谈", "我关心的是", "不重要", "不是重点", "那是你们的事"]
    deflect_count = sum(1 for u in target_utts if any(p in u["content"] for p in deflect_patterns))
    deflect_rate = round(deflect_count / n, 3)

    # 5. 人称偏好：用"我"vs"我们"vs"你们"的比例
    wo_count = all_text.count("我") - all_text.count("我们")
    women_count = all_text.count("我们")
    nimen_count = all_text.count("你们")
    total_person = wo_count + women_count + nimen_count or 1
    pronoun_bias = {
        "我(excl我们)": round(wo_count / total_person, 3),
        "我们": round(women_count / total_person, 3),
        "你们": round(nimen_count / total_person, 3),
    }

    # 6. 情绪烈度：感叹号和语气加重标记的频率
    exclamation_count = all_text.count("！") + all_text.count("!")
    emphasis_count = sum(1 for _ in re.finditer(r'(对对|不是不是|我我|这个这个|好好好)', all_text))
    emotion_intensity = round((exclamation_count + emphasis_count) / total_kchars, 2)

    decision_rules = _build_decision_rules(target_utts, conclusion_first_rate, analogy_rate, strategic_rate)
    value_hierarchy = _build_value_hierarchy(target_utts)
    biases = _build_bias_signals(target_utts)

    return {
        "conclusion_first_rate": conclusion_first_rate,
        "analogy_rate": analogy_rate,
        "analogy_per_1k": analogy_per_1k,
        "strategic_elevation_rate": strategic_rate,
        "strategic_elevation_per_1k": strategic_per_1k,
        "deflection_rate": deflect_rate,
        "pronoun_bias": pronoun_bias,
        "emotion_intensity_per_1k": emotion_intensity,
        "decision_rules": decision_rules,
        "value_hierarchy": value_hierarchy,
        "bias_signals": biases,
        "interpretation": {
            "decision_style": "结论先行型" if conclusion_first_rate > 0.15 else "论证推导型",
            "reasoning_preference": "类比驱动" if analogy_rate > 0.1 else "逻辑推导",
            "topic_tendency": "战略拉高型" if strategic_rate > 0.1 else "细节讨论型",
            "authority_posture": "裁判/指令型" if pronoun_bias["我(excl我们)"] > 0.6 else "协商型",
        },
    }


def _build_decision_rules(target_utts: list[dict], conclusion_first_rate: float, analogy_rate: float, strategic_rate: float) -> list[dict]:
    text_samples = [u["content"].strip() for u in target_utts if u.get("content", "").strip()]
    rules = []

    if conclusion_first_rate > 0.15:
        evidence = [t for t in text_samples if re.match(r'^(我觉得|我认为|这个首先|这个就是|说白了|本质上|这个完全)', t)][:2]
        rules.append(
            {
                "rule": "先下判断，再补论据",
                "confidence": round(min(0.95, 0.45 + conclusion_first_rate), 2),
                "evidence": evidence,
            }
        )

    if strategic_rate > 0.1:
        evidence = [t for t in text_samples if any(k in t for k in ["关键是", "核心问题", "本质上", "底层逻辑"])][:2]
        rules.append(
            {
                "rule": "细节先降级，再上升到原则层",
                "confidence": round(min(0.95, 0.4 + strategic_rate), 2),
                "evidence": evidence,
            }
        )

    if analogy_rate > 0.1:
        evidence = [t for t in text_samples if any(k in t for k in ["当年", "以前", "就像", "类似"])][:2]
        rules.append(
            {
                "rule": "优先调用旧经验类比新问题",
                "confidence": round(min(0.95, 0.4 + analogy_rate), 2),
                "evidence": evidence,
            }
        )

    return rules


def _build_value_hierarchy(target_utts: list[dict]) -> list[dict]:
    values = []
    joined = " ".join(u["content"] for u in target_utts)

    value_rules = [
        ("控制与责任", ["谁负责", "owner", "我关心的是", "先把结论", "时间节点"]),
        ("结果与效率", ["投入产出", "交付", "效率", "结果", "来不及"]),
        ("经验与资历", ["我年轻的时候", "当年", "以前", "我带团队"]),
        ("原则与判断权", ["本质上", "关键是", "方向不对", "核心问题"]),
    ]

    for value_name, keywords in value_rules:
        evidence = [u["content"] for u in target_utts if any(k in u["content"] for k in keywords)][:2]
        score = sum(joined.count(k) for k in keywords)
        if score > 0:
            values.append(
                {
                    "value": value_name,
                    "score": score,
                    "evidence": evidence,
                }
            )

    values.sort(key=lambda item: item["score"], reverse=True)
    return values


def _build_bias_signals(target_utts: list[dict]) -> list[dict]:
    bias_templates = [
        ("诉诸经验", ["我年轻的时候", "当年", "以前", "我带团队"]),
        ("过度简化", ["说白了", "本质上", "核心问题"]),
        ("控制者偏见", ["谁负责", "我关心的是", "先把结论"]),
    ]

    biases = []
    for bias_name, keywords in bias_templates:
        evidence = [u["content"] for u in target_utts if any(k in u["content"] for k in keywords)][:2]
        if evidence:
            biases.append(
                {
                    "bias": bias_name,
                    "confidence": round(min(0.95, 0.35 + len(evidence) * 0.2), 2),
                    "evidence": evidence,
                }
            )

    return biases


def main():
    parser = argparse.ArgumentParser(description="老登语料特征提取器")
    parser.add_argument("--input", "-i", required=True, help="source_parser.py 输出的 JSON 文件路径")
    parser.add_argument("--target-speaker", "-s", help="目标发言人（用于分析特定人物）")
    parser.add_argument("--markers", "-m", default=None, help="dimension_markers.json 路径")
    parser.add_argument("--output", "-o", default="-", help="输出文件路径 (默认 stdout)")
    parser.add_argument("--gap", type=int, default=60, help="分段间隔秒数 (默认 60)")

    args = parser.parse_args()

    # 加载语料
    if not os.path.exists(args.input):
        print(f"文件不存在: {args.input}", file=sys.stderr)
        sys.exit(1)

    with open(args.input, "r", encoding="utf-8") as f:
        utterances = json.load(f)

    # 加载标记词库
    markers = {}
    if args.markers and os.path.exists(args.markers):
        markers = load_markers(args.markers)
    else:
        # 尝试默认路径
        default_path = Path(__file__).parent / "dimension_markers.json"
        if default_path.exists():
            markers = load_markers(str(default_path))

    if not markers:
        print("警告: 未加载标记词库，部分功能不可用", file=sys.stderr)

    # 如果没有指定 target_speaker，取发言最多的人
    if not args.target_speaker:
        speaker_counts = Counter(u.get("speaker", "unknown") for u in utterances)
        args.target_speaker = speaker_counts.most_common(1)[0][0]
        print(f"未指定目标发言人，自动选择发言最多的: {args.target_speaker}", file=sys.stderr)

    target = args.target_speaker

    # 执行分析
    print(f"分析目标: {target} ({len([u for u in utterances if u.get('speaker') == target])} 条语料)", file=sys.stderr)

    speaker_stats = compute_speaker_stats(utterances, target)
    lexical = compute_lexical_features(utterances, target, markers)
    structural = compute_structural_features(utterances, target)
    behavioral = compute_behavioral_markers(utterances, target, markers)
    auto_weights = compute_auto_weights(behavioral, structural, lexical, markers)
    archetype = detect_archetype(auto_weights, utterances, target, markers)
    episodes = segment_episodes(utterances, target, args.gap)
    speaker_ranking = compare_speakers(utterances, markers)
    cognitive_proxies = compute_cognitive_proxies(utterances, target)

    # 汇总输出
    result = {
        "target_speaker": target,
        "total_utterances": len(utterances),
        "speaker_stats": {k: v for k, v in speaker_stats.items() if not k.startswith("_")},
        "speaker_ranking": speaker_ranking,
        "lexical_features": lexical,
        "structural_features": structural,
        "behavioral_markers": behavioral,
        "auto_weights": auto_weights,
        "archetype_detection": archetype,
        "cognitive_proxies": cognitive_proxies,
        "scene_modes": episodes,
    }

    output_json = json.dumps(result, ensure_ascii=False, indent=2)

    if args.output == "-":
        print(output_json)
    else:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output_json)
        print(f"特征提取完成，输出到 {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
