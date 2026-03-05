#!/usr/bin/env python3
"""Validate pinned agency-agents repertoire integration.

Checks:
- submodule exists and is initialized
- submodule HEAD matches pinned commit
- exactly 51 agent markdown files across expected divisions
- each agent file has frontmatter keys: name, description, color
- local markdown links inside submodule resolve
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SUBMODULE = ROOT / "external" / "agency-agents"
PINNED_COMMIT = "c6c51b4"

EXPECTED_DIVISION_COUNTS = {
    "engineering": 7,
    "design": 6,
    "marketing": 8,
    "product": 3,
    "project-management": 5,
    "testing": 7,
    "support": 6,
    "spatial-computing": 6,
    "specialized": 3,
}

REQUIRED_FRONTMATTER_KEYS = ("name", "description", "color")


def run_git(args: list[str], cwd: Path) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=str(cwd),
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def parse_frontmatter(text: str) -> str | None:
    if not text.startswith("---\n"):
        return None
    match = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    if not match:
        return None
    return match.group(1)


def has_key(frontmatter: str, key: str) -> bool:
    return re.search(rf"(?m)^{re.escape(key)}\s*:", frontmatter) is not None


def is_external_link(target: str) -> bool:
    return target.startswith(("http://", "https://", "mailto:", "#"))


def validate_local_links(md_path: Path, text: str, errors: list[str]) -> None:
    for match in re.finditer(r"\[[^\]]+\]\(([^)]+)\)", text):
        raw_target = match.group(1).strip()
        if not raw_target:
            continue
        # Handle optional title pattern: path "title"
        target = raw_target.split()[0]
        target = target.split("#", 1)[0]
        if not target or is_external_link(target):
            continue
        resolved = (md_path.parent / target).resolve()
        if not resolved.exists():
            rel_md = md_path.relative_to(SUBMODULE)
            errors.append(f"broken link '{raw_target}' in {rel_md}")


def main() -> int:
    errors: list[str] = []

    if not SUBMODULE.exists():
        errors.append("missing submodule path: external/agency-agents")
    else:
        git_dir = SUBMODULE / ".git"
        if not git_dir.exists():
            errors.append("submodule not initialized: external/agency-agents/.git missing")
        else:
            try:
                head = run_git(["rev-parse", "HEAD"], SUBMODULE)
                if not head.startswith(PINNED_COMMIT):
                    errors.append(
                        f"submodule commit mismatch: expected {PINNED_COMMIT}, found {head}"
                    )
            except Exception as exc:  # pragma: no cover - defensive path
                errors.append(f"unable to read submodule commit: {exc}")

    total = 0
    if SUBMODULE.exists():
        for division, expected_count in EXPECTED_DIVISION_COUNTS.items():
            division_path = SUBMODULE / division
            if not division_path.exists():
                errors.append(f"missing division directory: {division}")
                continue
            files = sorted(division_path.glob("*.md"))
            count = len(files)
            total += count
            if count != expected_count:
                errors.append(
                    f"division count mismatch for {division}: expected {expected_count}, found {count}"
                )
            for file_path in files:
                text = file_path.read_text(encoding="utf-8", errors="ignore")
                frontmatter = parse_frontmatter(text)
                rel = file_path.relative_to(SUBMODULE)
                if frontmatter is None:
                    errors.append(f"missing or malformed frontmatter in {rel}")
                    continue
                missing_keys = [k for k in REQUIRED_FRONTMATTER_KEYS if not has_key(frontmatter, k)]
                if missing_keys:
                    errors.append(f"missing frontmatter keys {missing_keys} in {rel}")

        if total != 51:
            errors.append(f"total agent count mismatch: expected 51, found {total}")

        for md_path in sorted(SUBMODULE.rglob("*.md")):
            text = md_path.read_text(encoding="utf-8", errors="ignore")
            validate_local_links(md_path, text, errors)

    if errors:
        print("SUB-AGENT REPERTOIRE VALIDATION FAILED")
        for issue in errors:
            print(f"- {issue}")
        return 1

    print("SUB-AGENT REPERTOIRE VALIDATION PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
