"""Validate the intentionally public boundary of the Athenaeum repository."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MAX_FILE_BYTES = 10 * 1024 * 1024
PRIVATE_FILENAMES = {
    ".env",
    "id_dsa",
    "id_ecdsa",
    "id_ed25519",
    "id_rsa",
}
PRIVATE_SUFFIXES = {".key", ".p12", ".pem", ".pfx"}
TEXT_SUFFIXES = {
    "",
    ".cfg",
    ".ini",
    ".json",
    ".md",
    ".py",
    ".toml",
    ".txt",
    ".yaml",
    ".yml",
}
CREDENTIAL_PATTERNS = {
    "private key": re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    "GitHub token": re.compile(r"gh[pousr]_[A-Za-z0-9_]{20,}"),
    "AWS access key": re.compile(r"AKIA[0-9A-Z]{16}"),
    "secret assignment": re.compile(
        r"(?i)(?:api[_-]?key|client[_-]?secret|access[_-]?token|password)"
        r"\s*[:=]\s*['\"]?[^\s'\"]{8,}"
    ),
}


def tracked_paths() -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=ROOT,
        check=True,
        stdout=subprocess.PIPE,
    )
    return [ROOT / item.decode("utf-8") for item in result.stdout.split(b"\0") if item]


def main() -> int:
    problems: list[str] = []
    paths = tracked_paths()

    if not (ROOT / "README.md").is_file():
        problems.append("README.md is missing")

    for path in paths:
        relative = path.relative_to(ROOT)
        lowered_parts = tuple(part.lower() for part in relative.parts)

        if path.is_symlink():
            problems.append(f"symbolic link is tracked: {relative}")
            continue
        if lowered_parts and lowered_parts[0] == "dna-analysis":
            problems.append(f"sensitive DNA path is tracked: {relative}")
            continue
        if path.name.lower() in PRIVATE_FILENAMES or path.suffix.lower() in PRIVATE_SUFFIXES:
            problems.append(f"private-looking file is tracked: {relative}")
        if path.stat().st_size > MAX_FILE_BYTES:
            problems.append(f"file exceeds 10 MiB: {relative}")
        if path.suffix.lower() not in TEXT_SUFFIXES:
            continue

        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            problems.append(f"expected UTF-8 text: {relative}")
            continue

        for label, pattern in CREDENTIAL_PATTERNS.items():
            if pattern.search(content):
                problems.append(f"possible {label} in {relative}")

    if problems:
        for problem in problems:
            print(f"ERROR: {problem}")
        return 1

    print(f"Validated {len(paths)} tracked public files; DNA, secret, and size checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
