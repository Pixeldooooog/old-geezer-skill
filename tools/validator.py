#!/usr/bin/env python3
"""
老登 Skill 质量验证器

对比特征统计数据和生成的 SKILL.md，输出保真度评分和矛盾项。
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path


def load_features(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_skill(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def validate_catchphrases(skill_text: str, features: dict) -> dict:
    """验证口头禅是否存在于 top n-gram 中"""
    candidates = features.get("lexical_features", {}).get("catchphrase_candidates", [])
    candidate_phrases = {c["phrase"] for c in candidates}

    # 从 SKILL.md 提取引号内的口头禅
    quoted = re.findall(r'"([^"]{2,20})"', skill_text)
    quoted += re.findall(r'"([^"]{2,20})"', skill_text)
    quoted += re.findall(r'「([^」]{2,20})」', skill_text)

    # 去重
    claimed_catchphrases = list(set(quoted))

    matched = []
    unmatched = []
    for phrase in claimed_catchphrases:
        # 检查是否在候选中或源数据中有
        found = False
        for cand in candidates:
            if phrase in cand["phrase"] or cand["phrase"] in phrase:
                found = True
                matched.append({"phrase": phrase, "matched_with": cand["phrase"], "count": cand["count"]})
                break
        if not found:
            unmatched.append(phrase)

    score = round(len(matched) / (len(claimed_catchphrases) or 1) * 100)

    return {
        "score": score,
        "claimed_count": len(claimed_catchphrases),
        "matched_count": len(matched),
        "matched": matched,
        "unmatched": unmatched,
    }


def validate_weights(skill_text: str, features: dict) -> dict:
    """验证 SKILL.md 中描述的强度是否与统计数据一致"""
    auto_weights = features.get("auto_weights", {})
    behavioral = features.get("behavioral_markers", {})

    results = {}
    contradictions = []

    # 检查 SKILL.md 中对每个维度的描述强度
    intensity_map = {
        "极高": 5, "非常高": 5, "频繁": 4, "很高": 4, "较高": 4,
        "适中": 3, "中等": 3, "偶尔": 2, "较少": 2, "很少": 1, "极低": 1,
    }

    for dim_name, weight in auto_weights.items():
        # 在 SKILL.md 中搜索相关描述
        dim_patterns = {
            "interruption": ["打断", "插话", "截断"],
            "lecturing": ["说教", "教育"],
            "bluffing": ["不懂装懂", "模糊", "回避"],
            "questioning": ["反问", "质问"],
            "tone_density": ["语气词", "填充词"],
            "profanity": ["粗口", "脏话"],
            "name_dropping": ["人脉", "炫耀"],
            "glory_days": ["当年", "过去"],
        }

        patterns = dim_patterns.get(dim_name, [dim_name])
        described_level = None

        for pattern in patterns:
            # 查找描述附近的强度词
            matches = re.finditer(pattern, skill_text)
            for m in matches:
                context = skill_text[max(0, m.start() - 30):m.end() + 30]
                for intensity_word, level in intensity_map.items():
                    if intensity_word in context:
                        described_level = level
                        break
                if described_level:
                    break
            if described_level:
                break

        if described_level:
            diff = abs(described_level - weight)
            status = "match" if diff <= 1 else "contradiction"
            if status == "contradiction":
                contradictions.append({
                    "dimension": dim_name,
                    "described_level": described_level,
                    "computed_weight": weight,
                    "issue": f"描述为{described_level}级但统计权重为{weight}",
                })
            results[dim_name] = {"described": described_level, "computed": weight, "status": status}
        else:
            results[dim_name] = {"described": None, "computed": weight, "status": "not_mentioned"}

    score = 100 - len(contradictions) * 15  # 每个矛盾扣 15 分
    score = max(0, score)

    return {
        "score": score,
        "dimensions": results,
        "contradictions": contradictions,
    }


def validate_fillers(skill_text: str, features: dict) -> dict:
    """验证填充词描述是否与统计数据一致"""
    filler_data = features.get("lexical_features", {}).get("filler_words", {})
    top_fillers = sorted(filler_data.items(), key=lambda x: -x[1].get("count", 0))[:5]
    top_filler_words = [w for w, _ in top_fillers]

    # 检查 SKILL.md 中是否提到了这些填充词
    mentioned = []
    missing = []
    for word in top_filler_words:
        if word in skill_text:
            mentioned.append(word)
        else:
            missing.append(word)

    score = round(len(mentioned) / (len(top_filler_words) or 1) * 100)

    return {
        "score": score,
        "top_fillers": top_filler_words,
        "mentioned": mentioned,
        "missing_from_skill": missing,
    }


def validate_question_ratio(skill_text: str, features: dict) -> dict:
    """验证反问描述是否与统计数据一致"""
    q_ratio = features.get("structural_features", {}).get("question_ratio", 0)

    # 检查 SKILL.md 中对反问频率的描述
    high_keywords = ["极高", "非常", "频繁", "大量", "几乎每"]
    low_keywords = ["较少", "偶尔", "很少", "不高"]
    medium_keywords = ["适中", "中等", "一定"]

    described = "unknown"
    for kw in high_keywords:
        if kw in skill_text and ("反问" in skill_text or "问句" in skill_text):
            described = "high"
            break
    if described == "unknown":
        for kw in low_keywords:
            if kw in skill_text and ("反问" in skill_text or "问句" in skill_text):
                described = "low"
                break
    if described == "unknown":
        for kw in medium_keywords:
            if kw in skill_text and ("反问" in skill_text or "问句" in skill_text):
                described = "medium"
                break

    # 实际判断
    if q_ratio > 0.3:
        actual = "high"
    elif q_ratio > 0.15:
        actual = "medium"
    else:
        actual = "low"

    match = described == actual or described == "unknown"

    return {
        "score": 100 if match else 40,
        "question_ratio": q_ratio,
        "described_level": described,
        "actual_level": actual,
        "match": match,
    }


def validate_archetype(skill_text: str, features: dict) -> dict:
    """验证 SKILL.md 中的原型描述是否与检测结果一致"""
    detection = features.get("archetype_detection", {})
    primary = detection.get("primary", {}).get("type", "")
    secondary = detection.get("secondary", {}).get("type", "")

    archetype_names = {
        "workplace": ["职场", "老板", "领导"],
        "banquet": ["酒桌", "饭局"],
        "relative": ["亲戚"],
        "taxi": ["出租车", "司机"],
        "internet": ["网络", "键盘"],
        "tech_veteran": ["技术", "老技术"],
    }

    primary_mentioned = False
    secondary_mentioned = False

    primary_aliases = archetype_names.get(primary, [primary])
    secondary_aliases = archetype_names.get(secondary, [secondary])

    for alias in primary_aliases:
        if alias in skill_text:
            primary_mentioned = True
            break
    for alias in secondary_aliases:
        if alias in skill_text:
            secondary_mentioned = True
            break

    return {
        "score": (100 if primary_mentioned else 50) + (25 if secondary_mentioned else 0),
        "detected_primary": primary,
        "detected_secondary": secondary,
        "primary_in_skill": primary_mentioned,
        "secondary_in_skill": secondary_mentioned,
    }


def validate_cognitive_rules(skill_text: str, features: dict) -> dict:
    """验证深层认知规则是否落进生成的 skill。"""
    proxies = features.get("cognitive_proxies", {})
    decision_rules = proxies.get("decision_rules", [])
    value_hierarchy = proxies.get("value_hierarchy", [])
    bias_signals = proxies.get("bias_signals", [])

    missing_rules = [item["rule"] for item in decision_rules if item.get("rule") not in skill_text]
    missing_values = [item["value"] for item in value_hierarchy if item.get("value") not in skill_text]
    missing_biases = [item["bias"] for item in bias_signals if item.get("bias") not in skill_text]

    total = len(decision_rules) + len(value_hierarchy) + len(bias_signals) or 1
    matched = total - len(missing_rules) - len(missing_values) - len(missing_biases)
    score = round(matched / total * 100)

    return {
        "score": score,
        "missing_rules": missing_rules,
        "missing_values": missing_values,
        "missing_biases": missing_biases,
    }


def find_missing_features(skill_text: str, features: dict) -> list:
    """找出统计数据中有但 persona 中没描述的特征"""
    missing = []

    # 检查高密度行为标记
    behavioral = features.get("behavioral_markers", {})
    for dim, data in behavioral.items():
        if data.get("per_1k", 0) > 1.0:
            # 这个维度在数据中显著，检查 SKILL.md 中是否有描述
            dim_keywords = {
                "interruption": ["打断"],
                "lecturing": ["说教"],
                "bluffing": ["不懂装懂"],
                "questioning": ["反问"],
                "profanity": ["粗口"],
                "name_dropping": ["人脉"],
                "glory_days": ["当年"],
            }
            keywords = dim_keywords.get(dim, [])
            found = any(kw in skill_text for kw in keywords)
            if not found:
                missing.append({
                    "dimension": dim,
                    "per_1k": data["per_1k"],
                    "top_markers": list(data.get("detail", {}).keys())[:3],
                    "issue": f"数据中{dim}标记频率较高({data['per_1k']}/1k字)但SKILL.md中未描述",
                })

    # 检查高频收尾模式
    enders = features.get("structural_features", {}).get("top_enders", [])
    for e in enders[:5]:
        if e["count"] >= 5 and e["suffix"] not in skill_text:
            missing.append({
                "dimension": "style",
                "suffix": e["suffix"],
                "count": e["count"],
                "issue": f"高频收尾词\"{e['suffix']}\"({e['count']}次)未在SKILL.md中提及",
            })

    # 检查场景行为链
    scene_modes = features.get("scene_modes", [])
    for scene in scene_modes[:3]:
        scene_label = scene.get("scene_label", "")
        behavior_chain = scene.get("behavior_chain", [])
        if scene_label and scene_label not in skill_text:
            missing.append({
                "dimension": "scene_mode",
                "scene_label": scene_label,
                "issue": f"高频场景模式\"{scene_label}\"未在SKILL.md中提及",
            })
        missing_actions = [action for action in behavior_chain if action not in skill_text]
        if missing_actions:
            missing.append({
                "dimension": "behavior_chain",
                "scene_label": scene_label,
                "missing_actions": missing_actions,
                "issue": f"场景\"{scene_label}\"的行为链未充分落地: {', '.join(missing_actions)}",
            })

    return missing


def main():
    parser = argparse.ArgumentParser(description="老登 Skill 质量验证器")
    parser.add_argument("--features", "-f", required=True, help="feature_extractor.py 输出的 JSON")
    parser.add_argument("--skill", "-s", required=True, help="生成的 SKILL.md 文件路径")
    parser.add_argument("--output", "-o", default="-", help="输出文件路径 (默认 stdout)")

    args = parser.parse_args()

    features = load_features(args.features)
    skill_text = load_skill(args.skill)

    # 执行各项验证
    catchphrase_result = validate_catchphrases(skill_text, features)
    weight_result = validate_weights(skill_text, features)
    filler_result = validate_fillers(skill_text, features)
    question_result = validate_question_ratio(skill_text, features)
    archetype_result = validate_archetype(skill_text, features)
    missing = find_missing_features(skill_text, features)

    # 综合评分
    scores = [
        catchphrase_result["score"],
        weight_result["score"],
        filler_result["score"],
        question_result["score"],
        min(archetype_result["score"], 100),
    ]
    overall = round(sum(scores) / len(scores))

    grade = "A" if overall >= 90 else "B" if overall >= 75 else "C" if overall >= 60 else "D" if overall >= 40 else "F"

    result = {
        "overall_score": overall,
        "grade": grade,
        "catchphrase_validation": catchphrase_result,
        "weight_validation": weight_result,
        "filler_validation": filler_result,
        "question_validation": question_result,
        "archetype_validation": archetype_result,
        "missing_features": missing,
        "recommendations": [],
    }

    # 生成建议
    if catchphrase_result["score"] < 70:
        result["recommendations"].append("口头禅描述与统计数据匹配度低，建议检查是否遗漏了高频短语")
    if weight_result["contradictions"]:
        for c in weight_result["contradictions"]:
            result["recommendations"].append(f"维度'{c['dimension']}'描述与数据矛盾: {c['issue']}")
    if filler_result["missing_from_skill"]:
        result["recommendations"].append(f"以下高频填充词未在SKILL.md中提及: {filler_result['missing_from_skill']}")
    if missing:
        result["recommendations"].append(f"发现 {len(missing)} 个数据中显著但SKILL.md中未描述的特征")
    if not result["recommendations"]:
        result["recommendations"].append("生成质量良好，未发现显著问题")

    output_json = json.dumps(result, ensure_ascii=False, indent=2)

    if args.output == "-":
        print(output_json)
    else:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output_json)
        print(f"验证完成，评分: {overall}/100 ({grade})", file=sys.stderr)


if __name__ == "__main__":
    main()
