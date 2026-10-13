#!/usr/bin/env python3
"""Update the Creative Avatar user profile.

Run this after the user gives feedback on candidate topic ideas, so the
feedback is stored in the local profile:
- like     mark as interesting: record the like and accumulate interest signals
- dislike  ask for a new batch: record that this batch did not land
- redirect off track: record the direction drift, so the next round can correct it
- select   selected: the chosen topic becomes a cross-scenario interest preference

Usage:
    python3 update_profile.py --feedback like --topic "Public perceptions of the Roman Empire through the Civilization game series"
    python3 update_profile.py --feedback select --topic "your topic title" --scenario academic_paper
    python3 update_profile.py --feedback redirect --topic "your topic title" --query "a more actionable direction"

The profile defaults to ~/.creative-clone/profile.json. Data is stored only
locally and can be edited by hand at any time.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List

DEFAULT_PROFILE_PATH = Path.home() / ".creative-clone" / "profile.json"
MAX_HISTORY = 500        # History cap, so the list cannot grow without bound
MAX_SIGNAL_TOPICS = 50   # Cap per signal type (only the most recent signals are kept)
FEEDBACK_CHOICES = ("like", "dislike", "redirect", "select")


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def minimal_profile() -> Dict:
    """Minimal profile skeleton, used only when both the profile and the template file are missing."""
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
    """Initialize the profile automatically when it does not exist, so the script does not fail on a missing file."""
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
    print("No profile found, initialized one automatically: {}".format(profile_path))
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
        # A selected topic becomes a cross-scenario interest: written into base.interests and preferences
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
    parser = argparse.ArgumentParser(description="Update the Creative Avatar user profile.")
    parser.add_argument(
        "--feedback",
        required=True,
        choices=FEEDBACK_CHOICES,
        help="Feedback type: like (mark as interesting) / dislike (ask for a new batch) / redirect (off track) / select (selected)",
    )
    parser.add_argument("--topic", required=True, type=str, help="The topic idea from this round")
    parser.add_argument(
        "--scenario",
        type=str,
        default="unknown",
        help="Scenario ID (e.g. academic_paper; default: unknown)",
    )
    parser.add_argument("--query", type=str, default="", help="Summary of the user's original request (optional)")
    parser.add_argument(
        "--path",
        type=str,
        default=None,
        help="Path to the profile file (default: ~/.creative-clone/profile.json)",
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

    print("Profile updated: {}".format(profile_path))
    print("Feedback type: {} | Topic: {}".format(args.feedback, topic))
    print("All profile data is stored locally and can be edited or deleted by hand at any time.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
