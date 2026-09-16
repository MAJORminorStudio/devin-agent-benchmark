#!/usr/bin/env python3
"""Fail-closed scan of tracked benchmark content before public release.

This checker reports filenames and line numbers only; it never prints matched
content. It intentionally excludes itself because its rule literals contain
the patterns it is designed to detect.
"""

from __future__ import annotations

import ipaddress
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, Iterable, List, Tuple


ROOT = Path(__file__).resolve().parents[1]
SELF = Path(__file__).resolve()
PERSONAL_IDENTIFIERS = ("dip" + "po", "0x" + "dip" + "po")

RULES: Dict[str, re.Pattern[str]] = {
    "absolute_path": re.compile(
        r"/(?:Volumes|Users|home)/|/private/(?:var/folders|tmp)(?:/|[\"'])|/var/folders/|[A-Za-z]:\\Users\\"
    ),
    "private_execution_path": re.compile(r"(?i)(?:\.benchmarks/\S+|private-run-store/\S+)"),
    "mac_address": re.compile(r"(?i)(?:[0-9a-f]{2}[:-]){5}[0-9a-f]{2}"),
    "credential_or_secret": re.compile(
        r"(?i)(?:ghp_[A-Za-z0-9_]{20,}|github_pat_[A-Za-z0-9_]{20,}|"
        r"sk-[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}|xox[baprs]-[A-Za-z0-9-]{10,}|"
        r"Bearer\s+[A-Za-z0-9._-]{20,}|(?:Cookie|Set-Cookie):\s*\S+|"
        r"-----BEGIN [A-Z ]*PRIVATE KEY-----|https?://[^/\s:@]+:[^@/\s]+@)"
    ),
    "private_email": re.compile(
        r"(?i)\b(?:0x)?[A-Za-z0-9._-]+@(?:gmail|icloud|protonmail|outlook|hotmail)\.[A-Za-z]{2,}\b"
    ),
    "private_ip": re.compile(r"(?<![\w.])(?:\d{1,3}\.){3}\d{1,3}(?![\w.])"),
    "hostname": re.compile(r"(?i)\bHOSTNAME\s*="),
    "personal_identifier": re.compile(
        r"(?i)\b(?:" + "|".join(map(re.escape, PERSONAL_IDENTIFIERS)) + r")\b"
    ),
    "operational_detail": re.compile(
        r"(?i)(?:Obsidian vault|Supabase project|research database|research pipeline|production repositor)"
    ),
    "obsolete_repository": re.compile("devin-agent-" + "cases"),
}


def tracked_files(root: Path) -> Iterable[Path]:
    output = subprocess.check_output(["git", "-C", str(root), "ls-files", "-z"])
    for raw in output.split(b"\0"):
        if raw:
            yield root / raw.decode("utf-8")


def is_private_ip(value: str) -> bool:
    try:
        address = ipaddress.ip_address(value)
    except ValueError:
        return False
    if address.is_loopback or address.is_unspecified or address.is_multicast:
        return False
    return address.is_private or address in ipaddress.ip_network("100.64.0.0/10")


def scan(root: Path = ROOT) -> List[Tuple[str, str, int]]:
    findings: List[Tuple[str, str, int]] = []
    for path in tracked_files(root):
        if path.resolve() == SELF:
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for line_number, line in enumerate(text.splitlines(), 1):
            for category, pattern in RULES.items():
                matches = list(pattern.finditer(line))
                if category == "private_ip":
                    matches = [match for match in matches if is_private_ip(match.group(0))]
                if matches:
                    findings.append((category, str(path.relative_to(root)), line_number))
    return findings


def main() -> int:
    findings = scan()
    if findings:
        print("Public-surface scan failed:")
        for category, path, line_number in findings:
            print(f"- {category}: {path}:{line_number}")
        print("Matched content is intentionally omitted from this report.")
        return 1
    print(f"Public-surface scan passed: {sum(1 for _ in tracked_files(ROOT)) - 1} tracked files checked.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
