#!/usr/bin/env python3
"""Validate engine outputs and scene profiles against JSON Schema files.

Usage:
    python3 validate_output.py                      # validate all scene profiles
    python3 validate_output.py --engine a output.json  # validate an engine A output
    python3 validate_output.py --engine b output.json  # validate an engine B output
    python3 validate_output.py --engine c output.json  # validate an engine C output
    python3 validate_output.py --profile ~/.creative-clone/profile.json  # validate a profile

Uses only the Python standard library. Checks required fields, types, and enums.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

SCHEMAS_DIR = Path(__file__).resolve().parent.parent / "schemas"
SCENES_DIR = Path(__file__).resolve().parent.parent / "assets" / "scene_profiles"

# Maps for quick lookup
ENGINE_SCHEMA_MAP = {
    "a": "engine_a_output.json",
    "b": "engine_b_output.json",
    "c": "engine_c_output.json",
    "saturation_scan": "engine_a_output.json",
    "cross_collision": "engine_b_output.json",
    "self_critique": "engine_c_output.json",
}

TYPE_MAP = {
    "string": str,
    "integer": int,
    "number": (int, float),
    "boolean": bool,
    "array": list,
    "object": dict,
    "null": type(None),
}

# Track if we printed any errors
_errors: List[str] = []


def _check_type(value: Any, expected: str) -> bool:
    if expected in TYPE_MAP:
        py_type = TYPE_MAP[expected]
        if expected == "null":
            return value is None
        return isinstance(value, py_type)
    return True


def _check_nullable(value: Any, expected: str) -> bool:
    """Check if value matches the type or is null (for nullable fields)."""
    if value is None:
        return True
    return _check_type(value, expected)


def _validate_required(data: Dict, required: List[str], path: str) -> None:
    for field in required:
        if field not in data:
            _errors.append("{}: missing required field '{}'".format(path, field))


def _check_type_field(data: Dict, field: str, expected: str, path: str, nullable: bool = False) -> None:
    if field not in data:
        return
    value = data[field]
    valid = _check_nullable(value, expected) if nullable else _check_type(value, expected)
    if not valid:
        got = type(value).__name__
        _errors.append("{}: field '{}' should be {}, got {}".format(path, field, expected, got))


def _check_enum(data: Dict, field: str, allowed: List[str], path: str) -> None:
    if field not in data:
        return
    if data[field] not in allowed:
        _errors.append("{}: field '{}' must be one of {}, got '{}'".format(
            path, field, allowed, data[field]))


def _check_range(data: Dict, field: str, minimum: float, maximum: float, path: str) -> None:
    if field not in data:
        return
    value = data[field]
    if isinstance(value, (int, float)):
        if value < minimum or value > maximum:
            _errors.append("{}: field '{}' must be between {} and {}, got {}".format(
                path, field, minimum, maximum, value))


# ---------------------------------------------------------------------------
# Engine A validator
# ---------------------------------------------------------------------------

def validate_engine_a(data: Dict, path: str = "engine_a") -> None:
    _validate_required(data, ["engine", "scanned_at", "domain", "saturation_report",
                              "saturated_topics", "gaps", "blacklist_hits", "evidence"], path)
    _check_enum(data, "engine", ["saturation_scan"], path)

    sr = data.get("saturation_report", [])
    if not isinstance(sr, list):
        _errors.append("{}: saturation_report must be an array".format(path))
        return
    for i, entry in enumerate(sr):
        sub = "{}.saturation_report[{}]".format(path, i)
        if not isinstance(entry, dict):
            _errors.append("{}: must be an object".format(sub))
            continue
        _validate_required(entry, ["topic", "saturation_score", "level", "reason"], sub)
        _check_range(entry, "saturation_score", 0, 100, sub)
        _check_enum(entry, "level", ["saturated", "hot", "gap", "blue_ocean"], sub)
        _check_enum(entry, "blacklist_type", ["over_saturated", "concept_stack", "none"], sub)

    ev = data.get("evidence", {})
    if isinstance(ev, dict):
        _validate_required(ev, ["checked", "real_time"], path + ".evidence")
        _check_type_field(ev, "checked", "boolean", path + ".evidence")
        _check_type_field(ev, "real_time", "boolean", path + ".evidence")


# ---------------------------------------------------------------------------
# Engine B validator
# ---------------------------------------------------------------------------

def validate_engine_b(data: Dict, path: str = "engine_b") -> None:
    _validate_required(data, ["engine", "generated_at", "base_domain", "candidates"], path)
    _check_enum(data, "engine", ["cross_collision"], path)

    candidates = data.get("candidates", [])
    if not isinstance(candidates, list) or len(candidates) < 1:
        _errors.append("{}: candidates must be a non-empty array".format(path))
        return
    for i, cand in enumerate(candidates):
        sub = "{}.candidates[{}]".format(path, i)
        if not isinstance(cand, dict):
            _errors.append("{}: must be an object".format(sub))
            continue
        _validate_required(cand, ["candidate_id", "title", "question", "why_link"], sub)
        wl = cand.get("why_link", "")
        if isinstance(wl, str) and len(wl.strip()) < 5:
            _errors.append("{}: why_link is too short (must explain the logical link)".format(sub))

    cp = data.get("collision_points", [])
    if isinstance(cp, list):
        for i, point in enumerate(cp):
            sub = "{}.collision_points[{}]".format(path, i)
            if not isinstance(point, dict):
                continue
            _validate_required(point, ["id", "a", "b", "logic_link", "why_link"], sub)
            _check_enum(point, "logic_link", ["strong", "medium", "loose"], sub)


# ---------------------------------------------------------------------------
# Engine C validator
# ---------------------------------------------------------------------------

def validate_engine_c(data: Dict, path: str = "engine_c") -> None:
    _validate_required(data, ["engine", "finished_at", "rounds_run", "verdicts", "final_candidates"], path)
    _check_enum(data, "engine", ["self_critique"], path)
    _check_range(data, "rounds_run", 1, 3, path)

    verdicts = data.get("verdicts", [])
    if isinstance(verdicts, list):
        for i, v in enumerate(verdicts):
            sub = "{}.verdicts[{}]".format(path, i)
            if not isinstance(v, dict):
                continue
            _validate_required(v, ["candidate_id", "final_verdict", "checklist"], sub)
            _check_enum(v, "final_verdict", ["pass", "reject"], sub)
            cl = v.get("checklist", [])
            if isinstance(cl, list):
                for j, item in enumerate(cl):
                    ssub = "{}.checklist[{}]".format(sub, j)
                    if isinstance(item, dict):
                        _check_enum(item, "item", ["C1", "C2", "C3", "C4", "C5", "C6"], ssub)


# ---------------------------------------------------------------------------
# Scene profile validator
# ---------------------------------------------------------------------------

def validate_scene_profile(data: Dict, path: str) -> None:
    _validate_required(data, ["scene_id", "scene_name", "scene_description",
                              "questionnaire_template", "tone_rules", "constraint_list",
                              "exclusion_rules"], path)

    sid = data.get("scene_id", "")
    if isinstance(sid, str) and not sid.replace("_", "").replace("0123456789", "").islower():
        _errors.append("{}: scene_id should be lowercase snake_case".format(path))

    qt = data.get("questionnaire_template", {})
    if isinstance(qt, dict):
        rounds = qt.get("rounds", [])
        if not isinstance(rounds, list) or len(rounds) < 1:
            _errors.append("{}: questionnaire_template.rounds must be a non-empty array".format(path))
        else:
            for i, rnd in enumerate(rounds):
                sub = "{}.rounds[{}]".format(path, i)
                if not isinstance(rnd, dict):
                    continue
                _validate_required(rnd, ["round_id", "round_title", "questions"], sub)
                questions = rnd.get("questions", [])
                if isinstance(questions, list):
                    for j, q in enumerate(questions):
                        ssub = "{}.questions[{}]".format(sub, j)
                        if isinstance(q, dict):
                            _validate_required(q, ["field", "question", "type", "required"], ssub)
                            _check_enum(q, "type", ["text", "choice", "multi_choice"], ssub)

    tr = data.get("tone_rules", {})
    if isinstance(tr, dict):
        _check_enum(tr, "base_tone", ["academic", "formal", "playful"], path + ".tone_rules")

    cl = data.get("constraint_list", [])
    if isinstance(cl, list) and len(cl) < 1:
        _errors.append("{}: constraint_list must have at least one entry".format(path))


# ---------------------------------------------------------------------------
# Profile validator
# ---------------------------------------------------------------------------

def validate_profile(data: Dict, path: str = "profile") -> None:
    _validate_required(data, ["schema_version", "profile_meta", "base", "preferences",
                              "weighted_topics", "feedback_log", "history", "signals",
                              "stats", "privacy"], path)

    sv = data.get("schema_version", 1)
    if isinstance(sv, int) and sv < 2:
        _errors.append("{}: schema_version is {}, consider migrating to v2".format(path, sv))

    wt = data.get("weighted_topics", [])
    if isinstance(wt, list):
        for i, entry in enumerate(wt):
            sub = "{}.weighted_topics[{}]".format(path, i)
            if isinstance(entry, dict):
                _validate_required(entry, ["topic", "weight", "last_feedback", "last_feedback_at"], sub)
                _check_range(entry, "weight", 0, 1, sub)
                _check_enum(entry, "last_feedback", ["like", "dislike", "redirect", "select"], sub)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def load_json(path: str) -> Dict:
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def validate_all_scenes() -> bool:
    """Validate all scene profile JSONs."""
    global _errors
    scene_schema_path = SCHEMAS_DIR / "scene_profile.json"
    if not scene_schema_path.exists():
        print("Schema file not found: {}".format(scene_schema_path))
        return False

    json_files = sorted(SCENES_DIR.glob("*.json"))
    if not json_files:
        print("No scene profile files found in {}".format(SCENES_DIR))
        return False

    total = 0
    passed = 0
    for fpath in json_files:
        total += 1
        _errors = []
        try:
            data = load_json(str(fpath))
        except json.JSONDecodeError as e:
            print("  FAIL  {} (invalid JSON: {})".format(fpath.name, e))
            continue
        validate_scene_profile(data, fpath.name)
        if _errors:
            print("  FAIL  {}".format(fpath.name))
            for err in _errors:
                print("        - {}".format(err))
        else:
            print("  PASS  {}".format(fpath.name))
            passed += 1

    print("\n{}: {}/{} scene profiles passed".format(
        "ALL PASS" if passed == total else "SOME FAILED", passed, total))
    return passed == total


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Validate engine outputs, scene profiles, and user profiles.")
    parser.add_argument("--engine", type=str, default=None,
                        help="Engine to validate (a/b/c or full name) + path to output JSON")
    parser.add_argument("--profile", type=str, default=None,
                        help="Path to a profile JSON to validate")
    parser.add_argument("--scenes", action="store_true",
                        help="Validate all scene profile JSONs")
    args = parser.parse_args()

    global _errors

    # Default: validate all scenes
    if not args.engine and not args.profile:
        return 0 if validate_all_scenes() else 1

    # Validate engine output
    if args.engine:
        parts = args.engine.split(None, 1)
        if len(parts) < 2:
            print("Usage: --engine <a|b|c> <path-to-output.json>")
            return 1
        eng_key, file_path = parts[0].lower(), parts[1]
        schema_name = ENGINE_SCHEMA_MAP.get(eng_key)
        if not schema_name:
            print("Unknown engine: {}. Use a/b/c or full name.".format(eng_key))
            return 1
        _errors = []
        try:
            data = load_json(file_path)
        except FileNotFoundError:
            print("File not found: {}".format(file_path))
            return 1
        except json.JSONDecodeError as e:
            print("Invalid JSON in {}: {}".format(file_path, e))
            return 1

        if schema_name == "engine_a_output.json":
            validate_engine_a(data, file_path)
        elif schema_name == "engine_b_output.json":
            validate_engine_b(data, file_path)
        elif schema_name == "engine_c_output.json":
            validate_engine_c(data, file_path)

        if _errors:
            print("FAIL: {} errors found".format(len(_errors)))
            for err in _errors:
                print("  - {}".format(err))
            return 1
        else:
            print("PASS: {} validates against {}".format(file_path, schema_name))
            return 0

    # Validate profile
    if args.profile:
        _errors = []
        try:
            data = load_json(args.profile)
        except FileNotFoundError:
            print("File not found: {}".format(args.profile))
            return 1
        except json.JSONDecodeError as e:
            print("Invalid JSON: {}".format(e))
            return 1
        validate_profile(data, args.profile)
        if _errors:
            print("FAIL: {} issues found".format(len(_errors)))
            for err in _errors:
                print("  - {}".format(err))
            return 1
        else:
            print("PASS: profile {} is valid (v{})".format(args.profile, data.get("schema_version", 1)))
            return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
