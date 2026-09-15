from collections.abc import Iterable


class Catalog:
    """Store records and provide a cached tag index."""

    def __init__(self) -> None:
        self._records: dict[str, dict[str, object]] = {}
        self._tag_cache: dict[str, tuple[str, ...]] = {}

    def add(self, record_id: str, *, tags: Iterable[str]) -> None:
        self._records[record_id] = {"tags": frozenset(tags)}
        self._tag_cache.clear()

    def discard(self, record_id: str) -> None:
        self._records.pop(record_id, None)

    def ids_for_tag(self, tag: str) -> tuple[str, ...]:
        cached = self._tag_cache.get(tag)
        if cached is None:
            cached = tuple(
                sorted(
                    record_id
                    for record_id, record in self._records.items()
                    if tag in record["tags"]
                )
            )
            self._tag_cache[tag] = cached
        return cached
