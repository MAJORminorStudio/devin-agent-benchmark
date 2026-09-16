from pathlib import Path


def discover_python_files(root: str | Path) -> list[str]:
    """Return Python files reachable from *root*, relative to that root."""
    base = Path(root).expanduser().resolve()
    found: list[str] = []
    for candidate in sorted(base.rglob("*.py")):
        resolved = candidate.resolve()
        if not str(resolved).startswith(str(base)):
            continue
        if resolved.is_file():
            found.append(candidate.relative_to(base).as_posix())
    return found
