#!/usr/bin/env python3
"""Initialize the Creative Avatar user profile.

Run this on first use to create the profile JSON file on the user's machine:
- Default path: ~/.creative-clone/profile.json
- Skips by default if the profile already exists (use --force to reinitialize;
  the old file is backed up as .bak first)
- Profile content comes from assets/profile_template.json; if the template is
  missing, a built-in minimal template is used as a fallback
- All data is stored locally and is never uploaded to any server

Usage:
    python3 init_profile.py
    python3 init_profile.py --path ~/my-profiles/profile.json
    python3 init_profile.py --force
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List

DEFAULT_PROFILE_PATH = Path.home() / ".creative-clone" / "profile.json"

# Built-in minimal template fallback: used only when assets/profile_template.json
# is missing. It mirrors the structure of assets/profile_template.json so the
# script can run even outside the repository directory.
FALLBACK_TEMPLATE: Dict = {
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

REQUIRED_TOP_LEVEL_KEYS = (
    "schema_version",
    "profile_meta",
    "base",
    "preferences",
    "history",
    "signals",
    "stats",
    "privacy",
)


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def default_template_path() -> Path:
    """The script lives under scripts/, so the template is at ../assets/profile_template.json."""
    return Path(__file__).resolve().parent.parent / "assets" / "profile_template.json"


def load_template(template_path: Path) -> Dict:
    if template_path.exists():
        with template_path.open("r", encoding="utf-8") as fh:
            data = json.load(fh)
        missing = [k for k in REQUIRED_TOP_LEVEL_KEYS if k not in data]
        if missing:
            raise SystemExit(
                "The template file is missing required fields: {} ({})".format(", ".join(missing), template_path)
            )
        return data
    # Deep-copy the fallback template so later edits do not mutate the module-level constant
    return json.loads(json.dumps(FALLBACK_TEMPLATE))


def write_profile(path: Path, data: Dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    with tmp_path.open("w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    tmp_path.replace(path)  # Atomic replace, so a partial write cannot corrupt the file


def build_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Initialize the Creative Avatar user profile file.")
    parser.add_argument(
        "--path",
        type=str,
        default=None,
        help="Path to the profile file (default: ~/.creative-clone/profile.json)",
    )
    parser.add_argument(
        "--template",
        type=str,
        default=None,
        help="Path to the template file (default: assets/profile_template.json)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite and rebuild when the profile already exists (backed up as .bak first)",
    )
    return parser.parse_args()


def main() -> int:
    args = build_args()
    profile_path = Path(args.path).expanduser() if args.path else DEFAULT_PROFILE_PATH
    template_path = (
        Path(args.template).expanduser() if args.template else default_template_path()
    )

    if profile_path.exists():
        if not args.force:
            print("Profile already exists, skipping initialization: {}".format(profile_path))
            print("Use --force to reinitialize (the old file is backed up as .bak first).")
            return 0
        backup_path = profile_path.with_suffix(profile_path.suffix + ".bak")
        profile_path.replace(backup_path)
        print("Backed up the existing profile: {}".format(backup_path))

    data = load_template(template_path)
    now = utc_now_iso()
    data.setdefault("profile_meta", {})["created_at"] = now
    data["profile_meta"]["updated_at"] = now
    write_profile(profile_path, data)

    print("Profile initialized: {}".format(profile_path))
    print("All profile data is stored locally and is never uploaded to any server. You can view, edit, or delete it at any time.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
