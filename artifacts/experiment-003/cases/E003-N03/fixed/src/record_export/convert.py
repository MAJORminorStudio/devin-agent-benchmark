from dataclasses import fields, is_dataclass
from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class Recipient:
    name: str
    email: str = field(metadata={"alias": "emailAddress"})


@dataclass(frozen=True)
class Line:
    sku: str
    quantity: int


@dataclass(frozen=True)
class Invoice:
    recipient: Recipient
    lines: tuple[Line, ...]
    note: str | None = None


def to_plain(value: Any, *, aliases: bool = True, omit_none: bool = False) -> Any:
    if is_dataclass(value) and not isinstance(value, type):
        result: dict[str, Any] = {}
        for item in fields(value):
            item_value = getattr(value, item.name)
            if omit_none and item_value is None:
                continue
            key = item.metadata.get("alias", item.name) if aliases else item.name
            result[key] = to_plain(item_value, aliases=aliases, omit_none=omit_none)
        return result
    if isinstance(value, Mapping):
        return {
            key: to_plain(item, aliases=aliases, omit_none=omit_none)
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [to_plain(item, aliases=aliases, omit_none=omit_none) for item in value]
    if isinstance(value, tuple):
        return tuple(to_plain(item, aliases=aliases, omit_none=omit_none) for item in value)
    return value
