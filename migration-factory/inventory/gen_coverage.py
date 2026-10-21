#!/usr/bin/env python3
"""Generate an operator-facing COVERAGE.md from APP_MANIFEST.yaml."""

from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path
from typing import Any

import yaml


EXPLICITLY_OUT = {"deferred", "rejected"}
IMPLEMENTATION_STATES = {"none", "partial", "full"}


def load_manifest(path: Path) -> dict[str, Any]:
    try:
        manifest = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as error:
        raise ValueError(f"Cannot read manifest {path}: {error}") from error

    if not isinstance(manifest, dict):
        raise ValueError(f"Manifest {path} must contain a YAML object")
    if not isinstance(manifest.get("behaviours"), list):
        raise ValueError(f"Manifest {path} must contain a behaviours list")
    return manifest


def validate_behaviours(behaviours: list[dict[str, Any]]) -> None:
    for behaviour in behaviours:
        if not isinstance(behaviour, dict):
            raise ValueError("Each behaviour must be a YAML object")

        behaviour_id = behaviour.get("behaviour_id", "<missing behaviour_id>")
        implementation = behaviour.get("impl_in_modern", "none")
        status = behaviour.get("status")

        if implementation not in IMPLEMENTATION_STATES:
            raise ValueError(
                f"{behaviour_id}: impl_in_modern must be none, partial, or full"
            )
        if status in {"converted", "verified"} and implementation != "full":
            raise ValueError(
                f"{behaviour_id}: status {status} requires impl_in_modern: full"
            )
        if implementation == "partial":
            if status not in {"accepted", "documented"}:
                raise ValueError(
                    f"{behaviour_id}: partial implementation must stay accepted or documented"
                )
            notes = behaviour.get("notes")
            if not isinstance(notes, str) or not notes.strip():
                raise ValueError(
                    f"{behaviour_id}: partial implementation requires gap notes"
                )


def render_coverage(manifest: dict[str, Any]) -> str:
    behaviours = manifest["behaviours"]
    validate_behaviours(behaviours)

    active = [
        behaviour
        for behaviour in behaviours
        if behaviour.get("status") not in EXPLICITLY_OUT
    ]
    done = [
        behaviour
        for behaviour in active
        if behaviour.get("impl_in_modern", "none") == "full"
    ]
    partial = [
        behaviour
        for behaviour in active
        if behaviour.get("impl_in_modern", "none") == "partial"
    ]
    remaining = [
        behaviour
        for behaviour in active
        if behaviour.get("impl_in_modern", "none") == "none"
    ]
    explicitly_out = [
        behaviour
        for behaviour in behaviours
        if behaviour.get("status") in EXPLICITLY_OUT
    ]

    lines = [
        f"# Coverage — {manifest.get('app_id', 'unknown app')}",
        "",
        "> **Generated from APP_MANIFEST.yaml. Never hand-edit.** "
        "Characterization flags (`legacy_green`) ≠ done in modern; "
        "use Operator progress for modern implementation.",
        "",
        "## Operator progress (modern implementation)",
        "",
        "| State | Count | Meaning |",
        "| --- | ---: | --- |",
        f"| none | {len(remaining)} | Not started in modern |",
        f"| partial | {len(partial)} | Some modern execution; gaps in notes |",
        f"| full (converted) | {len(done)} | Done in modern; parity may still be UNVERIFIED |",
        f"| deferred / rejected | {len(explicitly_out)} | Explicitly out |",
        "",
        "### Done in modern (impl_in_modern=full)",
        "",
    ]
    lines.extend(_named_behaviour_lines(done))
    lines.extend(["", "### Partial in modern", ""])
    lines.extend(_partial_behaviour_lines(partial))
    lines.extend(
        [
            "",
            "### Remaining (impl_in_modern none/absent, not deferred/rejected)",
            "",
        ]
    )
    lines.extend(_remaining_behaviour_lines(remaining))
    lines.extend(["", "## Inventory context", ""])
    lines.extend(_inventory_context(manifest))
    return "\n".join(lines) + "\n"


def _named_behaviour_lines(behaviours: list[dict[str, Any]]) -> list[str]:
    if not behaviours:
        return ["- None"]
    return [
        f"- {behaviour['behaviour_id']} — {behaviour.get('name') or '(unnamed)'}"
        for behaviour in behaviours
    ]


def _partial_behaviour_lines(behaviours: list[dict[str, Any]]) -> list[str]:
    if not behaviours:
        return ["- None"]
    return [
        f"- {behaviour['behaviour_id']} — {behaviour['notes'].strip()}"
        for behaviour in behaviours
    ]


def _remaining_behaviour_lines(behaviours: list[dict[str, Any]]) -> list[str]:
    if not behaviours:
        return ["- None"]
    return [
        f"- {behaviour['behaviour_id']} — "
        f"{behaviour.get('slice_id') or 'unassigned'} — "
        f"legacy_green {'yes' if behaviour.get('legacy_green', False) else 'no'}"
        for behaviour in behaviours
    ]


def _inventory_context(manifest: dict[str, Any]) -> list[str]:
    scanned_seeds = manifest.get("scanned_seeds", [])
    unscanned_hints = manifest.get("unscanned_hints", [])
    surfaces = manifest.get("surfaces", [])
    behaviours = manifest["behaviours"]
    surface_statuses = Counter(surface.get("status", "unknown") for surface in surfaces)
    behaviour_statuses = Counter(
        behaviour.get("status", "unknown") for behaviour in behaviours
    )

    lines = [
        "### Seeds",
        "",
        "| State | Count |",
        "| --- | ---: |",
        f"| scanned | {len(scanned_seeds)} |",
        f"| unscanned hints | {len(unscanned_hints)} |",
        "",
        "### Surface status histogram",
        "",
        "| Status | Count |",
        "| --- | ---: |",
    ]
    lines.extend(_histogram_rows(surface_statuses))
    lines.extend(
        [
            "",
            "### Behaviour status histogram",
            "",
            "| Status | Count |",
            "| --- | ---: |",
        ]
    )
    lines.extend(_histogram_rows(behaviour_statuses))
    lines.extend(
        [
            "",
            "### Characterization flags",
            "",
            "| Flag | Count |",
            "| --- | ---: |",
            f"| legacy_green | {sum(bool(item.get('legacy_green')) for item in behaviours)} |",
            f"| parity_green | {sum(bool(item.get('parity_green')) for item in behaviours)} |",
        ]
    )
    if unscanned_hints:
        lines.extend(["", "### Unscanned hints", ""])
        lines.extend(f"- {hint}" for hint in unscanned_hints)
    return lines


def _histogram_rows(histogram: Counter[str]) -> list[str]:
    if not histogram:
        return ["| none | 0 |"]
    return [f"| {state} | {count} |" for state, count in sorted(histogram.items())]


def resolve_manifest(target: str, repo_root: Path) -> Path:
    target_path = Path(target)
    if target_path.is_file():
        return target_path.resolve()
    return (repo_root / "inventory" / target / "APP_MANIFEST.yaml").resolve()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate COVERAGE.md from an application's APP_MANIFEST.yaml"
    )
    parser.add_argument("target", help="APP_ID or path to APP_MANIFEST.yaml")
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path.cwd(),
        help="Repository root containing inventory/<APP_ID> (default: current directory)",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    manifest_path = resolve_manifest(args.target, args.repo_root)
    if not manifest_path.is_file():
        raise SystemExit(f"APP_MANIFEST.yaml not found: {manifest_path}")

    coverage_path = manifest_path.with_name("COVERAGE.md")
    coverage_path.write_text(
        render_coverage(load_manifest(manifest_path)), encoding="utf-8"
    )
    print(coverage_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
