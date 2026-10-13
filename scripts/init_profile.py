#!/usr/bin/env python3
"""「创意分身」用户画像初始化脚本。

首次使用时运行，在用户本地创建画像 JSON 文件：
- 默认路径：~/.creative-clone/profile.json
- 画像已存在时默认跳过（可用 --force 重新初始化，旧文件先备份为 .bak）
- 画像内容来自 assets/profile_template.json；若模板缺失则使用内置最小模板兜底
- 所有数据仅保存在本地，不上传任何服务器

用法：
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

# 内置最小模板兜底：仅当 assets/profile_template.json 缺失时使用，
# 与 assets/profile_template.json 保持同构，便于脚本脱离仓库目录也能运行。
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
    """脚本位于 scripts/ 下，模板位于 ../assets/profile_template.json。"""
    return Path(__file__).resolve().parent.parent / "assets" / "profile_template.json"


def load_template(template_path: Path) -> Dict:
    if template_path.exists():
        with template_path.open("r", encoding="utf-8") as fh:
            data = json.load(fh)
        missing = [k for k in REQUIRED_TOP_LEVEL_KEYS if k not in data]
        if missing:
            raise SystemExit(
                "模板文件缺少必要字段：{}（{}）".format(", ".join(missing), template_path)
            )
        return data
    # 深拷贝兜底模板，避免后续修改污染模块级常量
    return json.loads(json.dumps(FALLBACK_TEMPLATE))


def write_profile(path: Path, data: Dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    with tmp_path.open("w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    tmp_path.replace(path)  # 原子替换，避免写一半损坏


def build_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="初始化「创意分身」用户画像文件。")
    parser.add_argument(
        "--path",
        type=str,
        default=None,
        help="画像文件路径（默认 ~/.creative-clone/profile.json）",
    )
    parser.add_argument(
        "--template",
        type=str,
        default=None,
        help="模板文件路径（默认 assets/profile_template.json）",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="画像已存在时覆盖重建（会先备份为 .bak）",
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
            print("画像已存在，跳过初始化：{}".format(profile_path))
            print("如需重新初始化，请加 --force（会先备份为 .bak）。")
            return 0
        backup_path = profile_path.with_suffix(profile_path.suffix + ".bak")
        profile_path.replace(backup_path)
        print("已备份旧画像：{}".format(backup_path))

    data = load_template(template_path)
    now = utc_now_iso()
    data.setdefault("profile_meta", {})["created_at"] = now
    data["profile_meta"]["updated_at"] = now
    write_profile(profile_path, data)

    print("画像已初始化：{}".format(profile_path))
    print("画像数据仅保存在本地，不上传任何服务器。可随时查看、编辑或删除。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
