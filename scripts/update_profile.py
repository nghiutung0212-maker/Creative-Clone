#!/usr/bin/env python3
"""「创意分身」用户画像更新脚本。

在用户对候选选题给出反馈后运行，把本次反馈沉淀进本地画像：
- like     「这个有意思」：记录喜欢，沉淀兴趣信号
- dislike  「换一批」：记录当前这批不满意
- redirect 「方向偏了」：记录方向偏差，供下一轮纠偏
- select   「最终选中」：选中选题沉淀为跨场景兴趣偏好

用法：
    python3 update_profile.py --feedback like --topic "《从<文明>系列游戏看大众对罗马帝国的认知偏差》"
    python3 update_profile.py --feedback select --topic "……" --scenario academic_paper
    python3 update_profile.py --feedback redirect --topic "……" --query "想换一个更落地的方向"

画像默认位于 ~/.creative-clone/profile.json，数据仅存本地，可随时手动编辑。
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List

DEFAULT_PROFILE_PATH = Path.home() / ".creative-clone" / "profile.json"
MAX_HISTORY = 500        # 历史记录上限，防止无限膨胀
MAX_SIGNAL_TOPICS = 50   # 每类信号主题上限（只保留最近信号）
FEEDBACK_CHOICES = ("like", "dislike", "redirect", "select")


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def minimal_profile() -> Dict:
    """极简画像骨架，仅在画像与模板文件都缺失时兜底。"""
    return {
        "schema_version": 1,
        "profile_meta": {
            "user_id": "local-anon",
            "created_at": None,
            "updated_at": None,
            "mode": "light",
        },
        "base": {
            "language": "zh-CN",
            "backgrounds": [],
            "interests": [],
            "resources": [],
            "writing_style": None,
            "thinking_depth": None,
        },
        "preferences": [],
        "history": [],
        "signals": {
            "liked_topics": [],
            "disliked_topics": [],
            "redirected_topics": [],
            "selected_topics": [],
        },
        "stats": {
            "total_sessions": 0,
            "like_count": 0,
            "dislike_count": 0,
            "redirect_count": 0,
            "select_count": 0,
        },
        "privacy": {
            "local_reading_enabled": False,
            "authorized_dirs": [],
            "consented_at": None,
            "consent_version": None,
            "last_reviewed_at": None,
        },
    }


def append_unique(items: List, value: str, limit: int = MAX_SIGNAL_TOPICS) -> None:
    if value in items:
        items.remove(value)
    items.append(value)
    del items[: max(0, len(items) - limit)]


def upsert_preference(
    profile: Dict, key: str, value: str, source: str, confidence: float, evidence: str
) -> None:
    now = utc_now_iso()
    prefs = profile.setdefault("preferences", [])
    for pref in prefs:
        if pref.get("key") == key:
            pref["value"] = value
            pref["source"] = source
            pref["confidence"] = max(pref.get("confidence", 0.0), confidence)
            pref["updated_at"] = now
            if evidence not in pref.setdefault("evidence", []):
                pref["evidence"].append(evidence)
            return
    prefs.append(
        {
            "key": key,
            "value": value,
            "confidence": confidence,
            "source": source,
            "scope": "cross_scenario",
            "scenario": None,
            "evidence": [evidence],
            "updated_at": now,
        }
    )


def write_profile(path: Path, data: Dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    with tmp_path.open("w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    tmp_path.replace(path)


def load_or_init_profile(profile_path: Path) -> Dict:
    """画像不存在时自动初始化，避免脚本因缺文件而失败。"""
    if profile_path.exists():
        with profile_path.open("r", encoding="utf-8") as fh:
            return json.load(fh)

    template_path = Path(__file__).resolve().parent.parent / "assets" / "profile_template.json"
    if template_path.exists():
        with template_path.open("r", encoding="utf-8") as fh:
            profile = json.load(fh)
    else:
        profile = minimal_profile()

    now = utc_now_iso()
    profile.setdefault("profile_meta", {})["created_at"] = now
    profile["profile_meta"]["updated_at"] = now
    profile_path.parent.mkdir(parents=True, exist_ok=True)
    write_profile(profile_path, profile)
    print("未找到画像，已自动初始化：{}".format(profile_path))
    return profile


def apply_feedback(
    profile: Dict, feedback: str, topic: str, scenario: str, query: str
) -> Dict:
    now = utc_now_iso()
    signals = profile.setdefault("signals", {})
    stats = profile.setdefault("stats", {})

    entry = {
        "scenario": scenario,
        "query": query,
        "topic": topic,
        "chosen_topics": [],
        "feedback": feedback,
        "timestamp": now,
    }

    if feedback == "like":
        append_unique(signals.setdefault("liked_topics", []), topic)
        stats["like_count"] = stats.get("like_count", 0) + 1
    elif feedback == "dislike":
        append_unique(signals.setdefault("disliked_topics", []), topic)
        stats["dislike_count"] = stats.get("dislike_count", 0) + 1
    elif feedback == "redirect":
        append_unique(signals.setdefault("redirected_topics", []), topic)
        stats["redirect_count"] = stats.get("redirect_count", 0) + 1
    elif feedback == "select":
        append_unique(signals.setdefault("selected_topics", []), topic)
        entry["chosen_topics"] = [topic]
        stats["select_count"] = stats.get("select_count", 0) + 1
        # 选中选题沉淀为跨场景兴趣：写入 base.interests 与 preferences
        interests = profile.setdefault("base", {}).setdefault("interests", [])
        append_unique(interests, topic)
        upsert_preference(
            profile, "selected_topic", topic, "explicit", 0.9, "{}:{}".format(scenario, now)
        )

    history = profile.setdefault("history", [])
    history.append(entry)
    del history[: max(0, len(history) - MAX_HISTORY)]

    profile.setdefault("profile_meta", {})["updated_at"] = now
    return profile


def build_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="更新「创意分身」用户画像。")
    parser.add_argument(
        "--feedback",
        required=True,
        choices=FEEDBACK_CHOICES,
        help="反馈类型：like（有意思）/ dislike（换一批）/ redirect（方向偏了）/ select（最终选中）",
    )
    parser.add_argument("--topic", required=True, type=str, help="本次选题内容")
    parser.add_argument(
        "--scenario",
        type=str,
        default="unknown",
        help="场景标识（如 academic_paper，默认 unknown）",
    )
    parser.add_argument("--query", type=str, default="", help="用户原始诉求摘要（可选）")
    parser.add_argument(
        "--path",
        type=str,
        default=None,
        help="画像文件路径（默认 ~/.creative-clone/profile.json）",
    )
    return parser.parse_args()


def main() -> int:
    args = build_args()
    profile_path = Path(args.path).expanduser() if args.path else DEFAULT_PROFILE_PATH
    topic = args.topic.strip()
    query = args.query.strip()

    profile = load_or_init_profile(profile_path)
    apply_feedback(profile, args.feedback, topic, args.scenario, query)
    write_profile(profile_path, profile)

    print("画像已更新：{}".format(profile_path))
    print("反馈类型：{} | 选题：{}".format(args.feedback, topic))
    print("画像数据仅保存在本地，可随时手动编辑或删除。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
