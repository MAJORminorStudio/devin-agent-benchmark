class TransactionParser:
    """Decode BEGIN/FIELD/COMMIT records from fragmented input."""

    def __init__(self) -> None:
        self._buffer = ""
        self._current: dict[str, object] | None = None

    def feed(self, chunk: str) -> list[dict[str, object]]:
        self._buffer += chunk
        records: list[dict[str, object]] = []
        while "\n" in self._buffer:
            line, self._buffer = self._buffer.split("\n", 1)
            records.extend(self._consume(line.rstrip("\r")))
        return records

    def _consume(self, line: str) -> list[dict[str, object]]:
        if line.startswith("BEGIN "):
            if self._current is None:
                self._current = {"id": line[6:], "fields": {}}
            return []
        if line.startswith("FIELD ") and self._current is not None:
            key, separator, value = line[6:].partition("=")
            if separator:
                fields = self._current["fields"]
                assert isinstance(fields, dict)
                fields[key] = value
            return []
        if line == "COMMIT" and self._current is not None:
            record = self._current
            self._current = None
            return [record]
        return []
