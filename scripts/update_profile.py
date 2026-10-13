#!/usr/bin/env python3
"""Update the Creative Avatar user profile with weighted feedback.

Weighted feedback model (v2):
  - select   +0.30  (strong positive: this topic becomes a cross-scenario interest)
  - like     +0.10  (weak positive: interesting, keep similar directions)
  - dislike  -0.20  (weak negative: this batch did not land)
  - redirect -0.40  (strong negative: direction drift, correct next round)

Rules:
  - Weights range from 0.0 to 1.0 (clamped, never negative for display).
  - Time decay: after 90 days without new feedback, weight is halved.
  - Idempotency: the same (topic, feedback) pair is only counted once.
  - Selected topics are also written into base.interests and preferences.

Usage:
    python3 update_profile.py --feedback like --topic "Public perceptions of the Roman Empire"
    python3 update_profile.py --feedback select --topic "your topic" --scenario academic_paper
    python3 update_profile.py --feedback redirect --topic "your topic" --query "a better direction"
    python3 update_profile.py --decay   # apply time-based decay to all weighted topics

The profile defaults to ~/.creative-clone/profile.json. Data is stored only
locally and can be edited by hand at any time.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

DEFAULT_PROFILE_PATH = Path.home() / ".creative-clone" / "profile.json"
MAX_HISTORY = 500
MAX_SIGNAL_TOPICS = 50
MAX_WEIGHTED_TOPICS = 200

# Weight deltas per feedback type
WEIGHT_DELTAS = {
    "select": 0.30,
    "like": 0.10,
    "dislike": -0.20,
    "redirect": -0.40,
}

# Decay: after this many days, halve the weight
DECAY_DAYS = 90
DECAY_FACTOR = 0.5

WEIGHT_MIN = 0.0
WEIGHT_MAX = 1.0

FEEDBACK_CHOICES = ("like", "dislike", "redirect", "select")


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def utc_now_dt() -> datetime:
    return datetime.now(timezone.utc)


def parse_iso(ts: str) -> Optional[datetime]:
    """Parse an ISO 8601 timestamp; return None on failure."""
    if not ts:
        return None
    try:
        return datetime.fromisoformat(ts)
    except (ValueError, TypeError):
        return None


def minimal_profile() -> Dict:
    """Minimal profile skeleton for v2."""
    return {
        "schema_version": 2,
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
        "weighted_topics": [],
        "feedback_log": [],
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
            "total_weighted_topics": 0,
            "avg_weight": 0.0,
        },
        "privacy": {
            "local_reading_enabled": False,
            "authorized_dirs": [],
            "consented_at": None,
            "consent_version": None,
            "last_reviewed_at": None,
        },
    }


def migrate_profile(profile: Dict) -> Dict:
    """Migrate a v1 profile to v2 by adding missing fields."""
    if profile.get("schema_version", 1) < 2:
        profile["schema_version"] = 2
        profile.setdefault("weighted_topics", [])
        profile.setdefault("feedback_log", [])
        stats = profile.setdefault("stats", {})
        stats.setdefault("total_weighted_topics", 0)
        stats.setdefault("avg_weight", 0.0)
    return profile


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
    if profile_path.exists():
        with profile_path.open("r", encoding="utf-8") as fh:
            profile = json.load(fh)
        profile = migrate_profile(profile)
        return profile

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


# ---------------------------------------------------------------------------
# Weighted topic logic
# ---------------------------------------------------------------------------

def find_weighted_topic(weighted: List[Dict], topic: str) -> Optional[Dict]:
    """Find a weighted topic entry by exact match (case-insensitive)."""
    lower = topic.lower()
    for entry in weighted:
        if entry.get("topic", "").lower() == lower:
            return entry
    return None


def is_duplicate_feedback(feedback_log: List[Dict], topic: str, feedback: str) -> bool:
    """Check if this exact (topic, feedback) pair was already recorded."""
    lower = topic.lower()
    for entry in feedback_log:
        if entry.get("topic", "").lower() == lower and entry.get("feedback") == feedback:
            return True
    return False


def apply_decay(weighted: List[Dict], now: datetime) -> int:
    """Apply time-based decay to all weighted topics. Returns count of decayed entries."""
    decayed = 0
    for entry in weighted:
        last_str = entry.get("last_feedback_at")
        last_dt = parse_iso(last_str) if last_str else None
        if last_dt is None:
            continue
        days_since = (now - last_dt).days
        if days_since >= DECAY_DAYS:
            old_weight = entry.get("weight", 0.0)
            new_weight = max(WEIGHT_MIN, old_weight * DECAY_FACTOR)
            if new_weight != old_weight:
                entry["weight"] = round(new_weight, 4)
                entry["last_decay_at"] = now.isoformat(timespec="seconds")
                decayed += 1
    return decayed


def update_weighted_topic(
    weighted: List[Dict],
    topic: str,
    feedback: str,
    now: datetime,
) -> None:
    """Create or update a weighted topic entry with the feedback delta."""
    entry = find_weighted_topic(weighted, topic)
    now_iso = now.isoformat(timespec="seconds")
    delta = WEIGHT_DELTAS.get(feedback, 0.0)

    if entry is None:
        entry = {
            "topic": topic,
            "weight": 0.0,
            "last_feedback": feedback,
            "last_feedback_at": now_iso,
            "last_decay_at": None,
            "feedback_history": [],
        }
        weighted.append(entry)

    # Apply decay before adding new weight (lazy decay on this topic)
    last_dt = parse_iso(entry.get("last_feedback_at", ""))
    if last_dt is not None:
        days_since = (now - last_dt).days
        if days_since >= DECAY_DAYS:
            entry["weight"] = round(entry.get("weight", 0.0) * DECAY_FACTOR, 4)
            entry["last_decay_at"] = now_iso

    # Apply the delta
    new_weight = max(WEIGHT_MIN, min(WEIGHT_MAX, entry.get("weight", 0.0) + delta))
    entry["weight"] = round(new_weight, 4)
    entry["last_feedback"] = feedback
    entry["last_feedback_at"] = now_iso

    # Record in feedback history (keep last 20 per topic)
    hist = entry.setdefault("feedback_history", [])
    hist.append({"feedback": feedback, "at": now_iso})
    del hist[: max(0, len(hist) - 20)]

    # Cap the weighted topics list
    if len(weighted) > MAX_WEIGHTED_TOPICS:
        # Drop the one with the lowest weight
        weighted.sort(key=lambda e: e.get("weight", 0.0), reverse=True)
        del weighted[MAX_WEIGHTED_TOPICS:]


def recalc_stats(profile: Dict) -> None:
    """Recalculate aggregate stats from weighted_topics."""
    weighted = profile.get("weighted_topics", [])
    stats = profile.setdefault("stats", {})
    if weighted:
        avg = sum(e.get("weight", 0.0) for e in weighted) / len(weighted)
        stats["total_weighted_topics"] = len(weighted)
        stats["avg_weight"] = round(avg, 4)
    else:
        stats["total_weighted_topics"] = 0
        stats["avg_weight"] = 0.0


def get_top_interests(profile: Dict, limit: int = 5) -> List[Dict]:
    """Return the top-N highest-weighted topics (for engine injection)."""
    weighted = profile.get("weighted_topics", [])
    sorted_topics = sorted(weighted, key=lambda e: e.get("weight", 0.0), reverse=True)
    return sorted_topics[:limit]


# ---------------------------------------------------------------------------
# Feedback application
# ---------------------------------------------------------------------------

def apply_feedback(
    profile: Dict, feedback: str, topic: str, scenario: str, query: str
) -> Dict:
    now_dt = utc_now_dt()
    now = now_dt.isoformat(timespec="seconds")
    signals = profile.setdefault("signals", {})
    stats = profile.setdefault("stats", {})
    weighted = profile.setdefault("weighted_topics", [])
    feedback_log = profile.setdefault("feedback_log", [])

    entry = {
        "scenario": scenario,
        "query": query,
        "topic": topic,
        "chosen_topics": [],
        "feedback": feedback,
        "timestamp": now,
    }

    # --- Idempotency check ---
    if is_duplicate_feedback(feedback_log, topic, feedback):
        print("Note: this exact feedback for this topic was already recorded; skipping weight update.")
    else:
        # --- Signal lists (legacy, kept for compatibility) ---
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
            interests = profile.setdefault("base", {}).setdefault("interests", [])
            append_unique(interests, topic)
            upsert_preference(
                profile, "selected_topic", topic, "explicit", 0.9, "{}:{}".format(scenario, now)
            )

        # --- Weighted topic update ---
        update_weighted_topic(weighted, topic, feedback, now_dt)

        # --- Feedback log (for idempotency) ---
        feedback_log.append({"topic": topic, "feedback": feedback, "at": now})
        del feedback_log[: max(0, len(feedback_log) - MAX_HISTORY)]

    # --- History ---
    history = profile.setdefault("history", [])
    history.append(entry)
    del history[: max(0, len(history) - MAX_HISTORY)]

    # --- Session counter (increment on first feedback of a session) ---
    stats["total_sessions"] = stats.get("total_sessions", 0)

    # --- Recalc aggregate stats ---
    recalc_stats(profile)

    profile.setdefault("profile_meta", {})["updated_at"] = now
    return profile


def apply_decay_command(profile: Dict) -> int:
    """Run time-based decay across all weighted topics. Returns count decayed."""
    weighted = profile.get("weighted_topics", [])
    count = apply_decay(weighted, utc_now_dt())
    recalc_stats(profile)
    profile.setdefault("profile_meta", {})["updated_at"] = utc_now_iso()
    return count


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Update the Creative Avatar user profile.")
    parser.add_argument(
        "--feedback",
        choices=FEEDBACK_CHOICES,
        default=None,
        help="Feedback type: like / dislike / redirect / select",
    )
    parser.add_argument("--topic", type=str, default=None, help="The topic idea from this round")
    parser.add_argument(
        "--scenario", type=str, default="unknown",
        help="Scenario ID (e.g. academic_paper; default: unknown)",
    )
    parser.add_argument("--query", type=str, default="", help="Summary of the user's original request")
    parser.add_argument(
        "--path", type=str, default=None,
        help="Path to the profile file (default: ~/.creative-clone/profile.json)",
    )
    parser.add_argument(
        "--decay", action="store_true",
        help="Apply time-based decay to all weighted topics and exit",
    )
    parser.add_argument(
        "--top-interests", type=int, default=None,
        help="Print the top-N highest-weighted topics and exit",
    )
    return parser.parse_args()


def main() -> int:
    args = build_args()
    profile_path = Path(args.path).expanduser() if args.path else DEFAULT_PROFILE_PATH

    profile = load_or_init_profile(profile_path)

    # --decay: apply time-based decay and exit
    if args.decay:
        count = apply_decay_command(profile)
        write_profile(profile_path, profile)
        print("Decay applied to {} topic(s).".format(count))
        print("Profile: {}".format(profile_path))
        return 0

    # --top-interests N: print top-N and exit
    if args.top_interests is not None:
        top = get_top_interests(profile, args.top_interests)
        if not top:
            print("No weighted topics yet.")
        else:
            print("Top {} weighted topics:".format(len(top)))
            for i, entry in enumerate(top, 1):
                print("  {}. [w={:.2f}] {}".format(i, entry.get("weight", 0.0), entry.get("topic", "")))
        return 0

    # Normal feedback mode
    if not args.feedback:
        print("Error: --feedback is required (or use --decay / --top-interests)")
        return 1
    if not args.topic:
        print("Error: --topic is required")
        return 1

    topic = args.topic.strip()
    query = args.query.strip()

    apply_feedback(profile, args.feedback, topic, args.scenario, query)
    write_profile(profile_path, profile)

    print("Profile updated: {}".format(profile_path))
    print("Feedback: {} | Topic: {}".format(args.feedback, topic))
    top = get_top_interests(profile, 3)
    if top:
        print("Top interests: " + " | ".join(
            "{} (w={:.2f})".format(e.get("topic", "")[:40], e.get("weight", 0.0)) for e in top
        ))
    print("All data is stored locally and can be edited or deleted by hand at any time.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
