#!/usr/bin/env python3
"""Bootstrap the migration factory in an application repository.

Copies the factory pack to migration-factory/, writes an incomplete
APP_MANIFEST.yaml, generates COVERAGE.md, and adds the Cursor rule.
Does not start Discovery and does not overwrite an existing manifest.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from datetime import date
from pathlib import Path

FACTORY_GIT_URL = "https://github.com/ptmfitch/migration-factory"
FACTORY_BRANCH = "main"
DEFAULT_HINT = "The estate is not scanned. Discovery has not started."
MANIFEST_NOTES = "Bootstrap only. No behaviours are known. Discovery has not started."
APP_ID_CHARS = set("abcdefghijklmnopqrstuvwxyz0123456789-")

ARTEFACT_DIRS = (
    "discovery",
    "testgen",
    "testexec",
    "architecture",
    "verification",
    "tests/characterization",
)

RULE_BODY = """---
description: >-
  Migration factory hard gate. Apply when the user works on Discovery,
  test generation, test execution, architecture PACK, Conversion,
  Verification, parity, goldens, APP_MANIFEST, COVERAGE, or a migration slice.
alwaysApply: false
---

# Migration factory

Before a factory stage, read `migration-factory/docs/FIELD-GUIDE.md` and the stage prompt and schema named in `migration-factory/docs/OPERATOR-RUNBOOK.md`.

Refuse the stage when those files are missing. Do not invent factory rules.

Write factory text and stakeholder text in ASD-STE100 only. Follow `migration-factory/skills/operator/asd-ste100/SKILL.md`.

Do not bind a MANIFEST or a PACK. A human bind is a git change.

Do not claim PARITY=GREEN. Only Verification COMPARE may claim parity.

Do not hand-edit `inventory/*/COVERAGE.md`. Regenerate it from `APP_MANIFEST.yaml` with `migration-factory/inventory/gen_coverage.py`.

Do not record goldens from modern code.

Leave `scanned_seeds` empty until Discovery walks those paths.

`factory-quick-start` only stands the pack up. Slice scoping is the next skill.
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--app-id", required=True, help="Kebab-case application id")
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path.cwd(),
        help="Application repository root (default: current directory)",
    )
    parser.add_argument(
        "--factory-src",
        type=Path,
        help="Local factory git root, or the inner migration-factory/ directory",
    )
    parser.add_argument(
        "--hint",
        action="append",
        default=[],
        help="Operator-stated unscanned residual. Repeat for more than one. "
        "Omit to record that the estate is not scanned.",
    )
    return parser.parse_args()


def fail(message: str) -> None:
    raise SystemExit(message)


def is_pack(path: Path) -> bool:
    return (
        (path / "docs" / "FIELD-GUIDE.md").is_file()
        and (path / "inventory" / "gen_coverage.py").is_file()
        and (path / "prompts" / "discovery-agent-v0.2.md").is_file()
    )


def is_control_plane(repo_root: Path) -> bool:
    readme = repo_root / "README.md"
    if not (readme.is_file() and is_pack(repo_root / "migration-factory")):
        return False
    for line in readme.read_text(encoding="utf-8").splitlines():
        if line.strip():
            return line.strip().lower().startswith("# migration factory")
    return False


def validate_app_id(app_id: str) -> None:
    if (
        not app_id
        or app_id[0] == "-"
        or app_id[-1] == "-"
        or "--" in app_id
        or any(char not in APP_ID_CHARS for char in app_id)
        or not app_id[0].isalpha()
    ):
        fail(
            "APP_ID must be kebab-case: a leading letter, then lowercase letters, "
            "digits, and single hyphens. Example: account-opening."
        )


def validate_hints(hints: list[str]) -> list[str]:
    cleaned = []
    for hint in hints:
        text = hint.strip()
        if not text:
            fail("A --hint value is empty. Omit --hint or pass a real residual.")
        cleaned.append(text)
    return cleaned or [DEFAULT_HINT]


def resolve_pack(source: Path) -> Path:
    source = source.expanduser().resolve()
    if is_pack(source):
        return source
    inner = source / "migration-factory"
    if is_pack(inner):
        return inner
    fail(
        f"{source} is not a factory pack.\n"
        "Pass the factory git root or the inner migration-factory/ directory."
    )


def pack_containing_script() -> Path | None:
    script = Path(__file__).resolve()
    if len(script.parents) < 4:
        return None
    candidate = script.parents[3]
    if is_pack(candidate):
        return candidate
    return None


def git_output(cwd: Path, args: list[str]) -> str | None:
    try:
        result = subprocess.run(
            ["git", "-C", str(cwd), *args],
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return None
    text = result.stdout.strip()
    return text or None


def ignore_junk(_directory: str, names: list[str]) -> set[str]:
    skipped = {"__pycache__", ".DS_Store", ".pytest_cache"}
    return {name for name in names if name in skipped or name.endswith(".pyc")}


def copy_tree(source: Path, dest: Path) -> None:
    shutil.copytree(source, dest, ignore=ignore_junk)


def write_vendor(dest: Path, source_label: str, commit: str) -> None:
    today = date.today().isoformat()
    dest.joinpath("VENDOR.txt").write_text(
        "Vendored factory pack.\n"
        f"source: {source_label}\n"
        f"commit: {commit}\n"
        f"vendored_on: {today}\n",
        encoding="utf-8",
    )


def vendor_local(source_pack: Path, dest: Path) -> None:
    copy_tree(source_pack, dest)
    write_vendor(
        dest,
        str(source_pack),
        git_output(source_pack, ["rev-parse", "HEAD"]) or "unknown",
    )


def vendor_clone(dest: Path) -> None:
    try:
        with tempfile.TemporaryDirectory(prefix="factory-pack-") as tmp:
            checkout = Path(tmp) / "src"
            subprocess.run(
                [
                    "git",
                    "clone",
                    "--depth",
                    "1",
                    "--branch",
                    FACTORY_BRANCH,
                    FACTORY_GIT_URL,
                    str(checkout),
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            inner = checkout / "migration-factory"
            if not is_pack(inner):
                fail("The clone did not contain the factory pack.")
            copy_tree(inner, dest)
            write_vendor(
                dest,
                FACTORY_GIT_URL,
                git_output(checkout, ["rev-parse", "HEAD"]) or "unknown",
            )
    except subprocess.CalledProcessError as error:
        detail = (error.stderr or error.stdout or "").strip()
        fail(
            "Cannot clone the factory pack.\n"
            f"{detail}\n"
            "Pass --factory-src with a local factory checkout, or retry with network access.\n"
            "Do not create the pack files by hand."
        )


def ensure_pack(repo_root: Path, factory_src: Path | None) -> str:
    dest = repo_root / "migration-factory"
    if is_pack(dest):
        return "present"
    if dest.exists():
        fail(
            "migration-factory/ exists but it is not the factory pack.\n"
            "Move that path aside and run the script again.\n"
            "The script does not merge into an existing directory."
        )
    source = resolve_pack(factory_src) if factory_src else pack_containing_script()
    if source is not None and source.resolve() == dest.resolve():
        return "present"
    if source is not None:
        vendor_local(source, dest)
        return "created"
    vendor_clone(dest)
    return "created"


def ensure_dir(repo_root: Path, relative: str) -> str:
    path = repo_root / relative
    path.mkdir(parents=True, exist_ok=True)
    if any(path.iterdir()):
        return "present"
    path.joinpath(".gitkeep").write_text("", encoding="utf-8")
    return "created"


def manifest_text(app_id: str, repo_url: str | None, hints: list[str]) -> str:
    hint_lines = "\n".join(f"  - {json.dumps(hint)}" for hint in hints)
    repo = "null" if repo_url is None else json.dumps(repo_url)
    today = date.today().isoformat()
    return (
        "schema_version: 1\n"
        f"app_id: {json.dumps(app_id)}\n"
        f"repo: {repo}\n"
        "status: in_progress\n"
        "completeness: incomplete\n"
        "scanned_seeds: []\n"
        "unscanned_hints:\n"
        f"{hint_lines}\n"
        "surfaces: []\n"
        "behaviours: []\n"
        f"last_updated: {json.dumps(today)}\n"
        "updated_by: factory-quick-start\n"
        f"notes: {json.dumps(MANIFEST_NOTES)}\n"
    )


def write_manifest(path: Path, app_id: str, repo_url: str | None, hints: list[str]) -> str:
    if path.is_file():
        return "present"
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".yaml.tmp")
    temporary.write_text(manifest_text(app_id, repo_url, hints), encoding="utf-8")
    temporary.replace(path)
    return "created"


def generate_coverage(repo_root: Path, app_id: str, manifest: Path) -> str:
    coverage = manifest.with_name("COVERAGE.md")
    if coverage.is_file():
        return "present"
    try:
        import yaml  # noqa: F401
    except ImportError:
        fail(
            "PyYAML is required to generate COVERAGE.md.\n"
            "Install it with: python3 -m pip install pyyaml\n"
            f"The manifest is at {manifest}.\n"
            "Do not hand-edit COVERAGE.md.\n"
            "Run this script again after PyYAML is installed."
        )
    generator = repo_root / "migration-factory" / "inventory" / "gen_coverage.py"
    result = subprocess.run(
        [sys.executable, str(generator), app_id, "--repo-root", str(repo_root)],
        cwd=repo_root,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        detail = (result.stderr or result.stdout or "").strip()
        fail(f"COVERAGE.md was not generated.\n{detail}")
    if not coverage.is_file():
        fail(f"COVERAGE.md was not generated at {coverage}.")
    return "created"


def write_rule(repo_root: Path) -> str:
    path = repo_root / ".cursor" / "rules" / "migration-factory.mdc"
    if path.is_file():
        return "present"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(RULE_BODY, encoding="utf-8")
    return "created"


def running_skill_dir() -> Path:
    return Path(__file__).resolve().parents[1]


def ensure_skill_in_pack(repo_root: Path) -> str:
    """Copy this drop-in skill into the pack when the published pack lacks it."""
    vendored = repo_root / "migration-factory" / "skills" / "factory-quick-start"
    if (vendored / "SKILL.md").is_file():
        return "present"
    running = running_skill_dir()
    if running.resolve() == vendored.resolve() or not (running / "SKILL.md").is_file():
        fail("The factory pack has no factory-quick-start skill.")
    vendored.parent.mkdir(parents=True, exist_ok=True)
    copy_tree(running, vendored)
    return "injected"


def install_cursor_skill(repo_root: Path) -> str:
    source = repo_root / "migration-factory" / "skills" / "factory-quick-start"
    dest = repo_root / ".cursor" / "skills" / "factory-quick-start"
    if (dest / "SKILL.md").is_file():
        return "present"
    if not (source / "SKILL.md").is_file():
        fail("The factory pack has no factory-quick-start skill.")
    if source.resolve() == dest.resolve():
        return "present"
    dest.parent.mkdir(parents=True, exist_ok=True)
    copy_tree(source, dest)
    return "created"


def cursor_is_ignored(repo_root: Path) -> bool:
    gitignore = repo_root / ".gitignore"
    if not gitignore.is_file():
        return False
    for line in gitignore.read_text(encoding="utf-8", errors="replace").splitlines():
        stripped = line.split("#", 1)[0].strip()
        if stripped in {".cursor", ".cursor/", ".cursor/**"}:
            return True
    return False


def application_repo_url(repo_root: Path) -> str | None:
    url = git_output(repo_root, ["remote", "get-url", "origin"])
    if url and "ptmfitch/migration-factory" in url:
        return None
    return url


def main() -> int:
    args = parse_args()
    validate_app_id(args.app_id)
    hints = validate_hints(args.hint)
    repo_root = args.repo_root.expanduser().resolve()
    if not repo_root.is_dir():
        fail(f"Repository root does not exist: {repo_root}")
    if is_pack(repo_root):
        fail(
            "This directory is the factory pack tree.\n"
            "Run the skill in the application repository.\n"
            "The script copies the pack to migration-factory/ inside that repository."
        )
    if is_control_plane(repo_root):
        fail(
            "This repository is the factory pack repository.\n"
            "Copy migration-factory/skills/factory-quick-start to the application "
            "repository at .cursor/skills/factory-quick-start.\n"
            "Run the skill there.\n"
            "Do not create an application inventory in the factory pack repository."
        )

    pack_status = ensure_pack(repo_root, args.factory_src)
    if not is_pack(repo_root / "migration-factory"):
        fail("The factory pack is not at migration-factory/.")
    pack_skill_status = ensure_skill_in_pack(repo_root)

    dir_created = [
        relative
        for relative in ARTEFACT_DIRS
        if ensure_dir(repo_root, relative) == "created"
    ]
    manifest = repo_root / "inventory" / args.app_id / "APP_MANIFEST.yaml"
    manifest_status = write_manifest(
        manifest, args.app_id, application_repo_url(repo_root), hints
    )
    rule_status = write_rule(repo_root)
    skill_status = install_cursor_skill(repo_root)
    coverage_status = generate_coverage(repo_root, args.app_id, manifest)

    print(f"BOOTSTRAP_STATUS: complete")
    print(f"APP_ID: {args.app_id}")
    print(f"PACK: {pack_status}")
    print(f"PACK_SKILL: {pack_skill_status}")
    print(f"MANIFEST: {manifest_status}")
    print(f"COVERAGE: {coverage_status}")
    print(f"RULE: {rule_status}")
    print(f"CURSOR_SKILL: {skill_status}")
    if dir_created:
        print("DIRS: created " + ", ".join(dir_created))
    else:
        print("DIRS: present")
    if cursor_is_ignored(repo_root):
        print(
            "WARNING: This repository ignores .cursor/. "
            "The rule works on this machine. It is not committed."
        )
    print("NEXT: Scope one slice with the slice-scoping skill. Do not start Discovery.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
