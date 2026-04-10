#!/usr/bin/env python3
"""
数据源解析器 —— 从各种格式提取老登语料

支持的数据源：
- 腾讯会议文字转写 (.docx)
- 微信聊天记录 (txt/html/csv)
- 飞书消息导出 (json/txt)
- 纯文本 / Markdown
- PDF
- 邮件 (.eml)
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path


SYSTEM_SPEAKERS = {"系统消息", "系统", "system", "wechat system"}
LOW_SIGNAL_CONTENT = {
    "收到", "好的", "嗯", "哦", "ok", "OK", "1", "好", "在", "👌", "收到。",
}


def normalize_speaker_name(raw_name: str) -> str:
    if not raw_name:
        return ""

    speaker = raw_name.strip().lstrip("@")
    speaker = speaker.replace("\u3000", " ")
    speaker = re.sub(r"\s+", " ", speaker)
    speaker = re.sub(r"[\(（][^()（）]{1,20}[\)）]\s*$", "", speaker).strip()
    speaker = re.sub(r"^\[[^\[\]]+\]\s*", "", speaker).strip()
    return speaker


def clean_content(text: str) -> str:
    if not text:
        return ""

    cleaned = text.replace("\r\n", "\n").replace("\r", "\n").strip()
    cleaned = re.sub(r"^引用[:：].*$", "", cleaned, flags=re.MULTILINE)
    cleaned = re.sub(r"^\[图片\]$", "", cleaned, flags=re.MULTILINE)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip()


def _parse_timestamp(timestamp: str) -> datetime | None:
    if not timestamp:
        return None

    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y/%m/%d %H:%M:%S"):
        try:
            return datetime.strptime(timestamp.strip(), fmt)
        except ValueError:
            continue
    return None


def is_noise_utterance(speaker: str, content: str) -> bool:
    normalized_speaker = speaker.lower().strip()
    normalized_content = content.strip()

    if normalized_speaker in {s.lower() for s in SYSTEM_SPEAKERS}:
        return True
    if "撤回了一条消息" in normalized_content:
        return True
    if normalized_content in LOW_SIGNAL_CONTENT:
        return True
    return False


def preprocess_utterances(utterances: list[dict], merge_gap_seconds: int = 30) -> list[dict]:
    """标准化 speaker/content，并合并连续短间隔发言。"""
    cleaned = []

    for utterance in utterances:
        speaker = normalize_speaker_name(str(utterance.get("speaker", "")))
        content = clean_content(str(utterance.get("content", "")))
        timestamp = str(utterance.get("timestamp", "")).strip()

        if not speaker or not content:
            continue
        if is_noise_utterance(speaker, content):
            continue

        current = {
            "speaker": speaker,
            "timestamp": timestamp,
            "content": content,
        }

        if not cleaned:
            cleaned.append(current)
            continue

        previous = cleaned[-1]
        if previous["speaker"] != current["speaker"]:
            cleaned.append(current)
            continue

        prev_dt = _parse_timestamp(previous.get("timestamp", ""))
        curr_dt = _parse_timestamp(current.get("timestamp", ""))
        within_gap = False
        if prev_dt and curr_dt:
            within_gap = (curr_dt - prev_dt).total_seconds() <= merge_gap_seconds
        elif not prev_dt or not curr_dt:
            within_gap = True

        if within_gap:
            previous["content"] = f"{previous['content']}\n{current['content']}".strip()
            if not previous.get("timestamp"):
                previous["timestamp"] = current["timestamp"]
        else:
            cleaned.append(current)

    return cleaned


def parse_tencent_meeting(file_path: str, target_speakers: list[str] | None = None) -> list[dict]:
    """解析腾讯会议文字转写 (.docx -> markdown via pandoc, 或直接 .md/.txt)"""
    ext = Path(file_path).suffix.lower()

    if ext == ".docx":
        import subprocess
        result = subprocess.run(
            ["pandoc", file_path, "-t", "markdown", "--wrap=none"],
            capture_output=True, text=True, check=True,
        )
        text = result.stdout
    else:
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()

    # 腾讯会议转写格式: "发言人 YYYY-MM-DD HH:MM:SS\n内容"
    pattern = re.compile(
        r"^(.+?)\s+(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})\s*\n\n(.*?)(?=\n\n.+?\s+\d{4}-\d{2}-\d{2}|\Z)",
        re.MULTILINE | re.DOTALL,
    )

    utterances = []
    for m in pattern.finditer(text):
        speaker = m.group(1).strip()
        timestamp = m.group(2).strip()
        content = m.group(3).strip()
        if not content:
            continue
        if target_speakers and speaker not in target_speakers:
            continue
        utterances.append({
            "speaker": speaker,
            "timestamp": timestamp,
            "content": content,
        })

    return utterances


def parse_wechat_txt(file_path: str, target_speakers: list[str] | None = None) -> list[dict]:
    """解析微信聊天记录导出 (txt 格式)
    
    常见格式:
    2026-04-08 12:00:00 张三
    消息内容
    
    或:
    张三 2026-04-08 12:00:00
    消息内容
    """
    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()

    # 尝试格式1: 时间在前
    pattern1 = re.compile(
        r"^(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})\s+(.+?)\s*\n(.*?)(?=\n\d{4}-\d{2}-\d{2}|\Z)",
        re.MULTILINE | re.DOTALL,
    )
    # 尝试格式2: 人名在前 (腾讯会议风格)
    pattern2 = re.compile(
        r"^(.+?)\s+(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})\s*\n(.*?)(?=\n.+?\s+\d{4}-\d{2}-\d{2}|\Z)",
        re.MULTILINE | re.DOTALL,
    )

    utterances = []

    matches1 = list(pattern1.finditer(text))
    matches2 = list(pattern2.finditer(text))
    
    if len(matches1) >= len(matches2):
        for m in matches1:
            speaker = m.group(2).strip()
            timestamp = m.group(1).strip()
            content = m.group(3).strip()
            if not content:
                continue
            if target_speakers and speaker not in target_speakers:
                continue
            utterances.append({"speaker": speaker, "timestamp": timestamp, "content": content})
    else:
        for m in matches2:
            speaker = m.group(1).strip()
            timestamp = m.group(2).strip()
            content = m.group(3).strip()
            if not content:
                continue
            if target_speakers and speaker not in target_speakers:
                continue
            utterances.append({"speaker": speaker, "timestamp": timestamp, "content": content})

    return utterances


def parse_feishu_json(file_path: str, target_speakers: list[str] | None = None) -> list[dict]:
    """解析飞书消息导出 (JSON 格式)"""
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    utterances = []
    messages = data if isinstance(data, list) else data.get("messages", data.get("data", []))

    for msg in messages:
        speaker = msg.get("sender", msg.get("from", msg.get("user", "")))
        content = msg.get("content", msg.get("text", msg.get("body", "")))
        timestamp = msg.get("time", msg.get("timestamp", msg.get("create_time", "")))

        if isinstance(content, dict):
            content = content.get("text", str(content))

        if not content or not speaker:
            continue
        if target_speakers and speaker not in target_speakers:
            continue

        utterances.append({"speaker": str(speaker), "timestamp": str(timestamp), "content": str(content)})

    return utterances


def parse_plain_text(file_path: str) -> list[dict]:
    """解析纯文本/Markdown —— 整个文件作为一段语料"""
    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()
    return [{"speaker": "unknown", "timestamp": "", "content": text}]


def parse_pdf(file_path: str) -> list[dict]:
    """解析 PDF 文件"""
    try:
        import subprocess
        result = subprocess.run(
            ["pdftotext", "-layout", file_path, "-"],
            capture_output=True, text=True, check=True,
        )
        text = result.stdout
    except FileNotFoundError:
        # fallback: 试试 python 库
        try:
            from PyPDF2 import PdfReader
            reader = PdfReader(file_path)
            text = "\n".join(page.extract_text() or "" for page in reader.pages)
        except ImportError:
            print("需要安装 pdftotext (poppler-utils) 或 PyPDF2 来解析 PDF", file=sys.stderr)
            sys.exit(1)

    return [{"speaker": "unknown", "timestamp": "", "content": text}]


def parse_email(file_path: str) -> list[dict]:
    """解析 .eml 邮件文件"""
    import email
    from email import policy

    with open(file_path, "rb") as f:
        msg = email.message_from_binary_file(f, policy=policy.default)

    sender = msg.get("From", "unknown")
    subject = msg.get("Subject", "")
    body = msg.get_body(preferencelist=("plain", "html"))
    content = body.get_content() if body else ""

    return [{"speaker": sender, "timestamp": msg.get("Date", ""), "content": f"[{subject}]\n{content}"}]


def parse_csv(file_path: str, target_speakers: list[str] | None = None) -> list[dict]:
    """解析 CSV 格式聊天记录 (需要 speaker/content 列)"""
    import csv

    utterances = []
    with open(file_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            speaker = row.get("speaker", row.get("sender", row.get("from", row.get("name", ""))))
            content = row.get("content", row.get("text", row.get("message", row.get("body", ""))))
            timestamp = row.get("timestamp", row.get("time", row.get("date", "")))
            if not content:
                continue
            if target_speakers and speaker not in target_speakers:
                continue
            utterances.append({"speaker": speaker, "timestamp": timestamp, "content": content})

    return utterances


# ── 自动检测格式并解析 ──

PARSERS = {
    ".docx": parse_tencent_meeting,
    ".txt": parse_wechat_txt,
    ".md": parse_plain_text,
    ".markdown": parse_plain_text,
    ".json": parse_feishu_json,
    ".pdf": parse_pdf,
    ".eml": parse_email,
    ".csv": parse_csv,
}


def auto_parse(file_path: str, target_speakers: list[str] | None = None) -> list[dict]:
    """根据文件扩展名自动选择解析器"""
    ext = Path(file_path).suffix.lower()
    parser = PARSERS.get(ext)
    if not parser:
        print(f"不支持的文件格式: {ext}，尝试按纯文本解析", file=sys.stderr)
        parser = parse_plain_text

    import inspect
    sig = inspect.signature(parser)
    if "target_speakers" in sig.parameters:
        return parser(file_path, target_speakers=target_speakers)
    return parser(file_path)


def main():
    parser = argparse.ArgumentParser(description="老登语料解析器")
    parser.add_argument("files", nargs="+", help="要解析的文件路径")
    parser.add_argument("--speakers", nargs="*", help="只提取指定发言人的内容")
    parser.add_argument("--output", "-o", default="-", help="输出文件路径 (默认 stdout)")
    parser.add_argument("--format", choices=["json", "text"], default="json", help="输出格式")

    args = parser.parse_args()

    all_utterances = []
    for fp in args.files:
        if not os.path.exists(fp):
            print(f"文件不存在: {fp}", file=sys.stderr)
            continue
        utterances = auto_parse(fp, target_speakers=args.speakers)
        all_utterances.extend(utterances)

    all_utterances = preprocess_utterances(all_utterances)

    if args.format == "json":
        output = json.dumps(all_utterances, ensure_ascii=False, indent=2)
    else:
        output = "\n\n".join(
            f"[{u['speaker']}] {u['content']}" for u in all_utterances
        )

    if args.output == "-":
        print(output)
    else:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"已输出 {len(all_utterances)} 条语料到 {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
