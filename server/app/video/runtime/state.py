from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

@dataclass
class RuntimeObject:
    id: str
    mobject: Any
    semantic_type: str
    state: dict[str, Any] = field(default_factory=dict)
    parent_id: str | None = None
    relations: list[dict[str, Any]] = field(default_factory=list)
    visible: bool = False

class ObjectRegistry:
    """Owns live semantic state and keeps attachments spatially coherent."""
    def __init__(self):
        self._objects: dict[str, RuntimeObject] = {}
        self._attachments: dict[str, list[str]] = {}

    def add(self, entry: RuntimeObject) -> RuntimeObject:
        if entry.id in self._objects:
            raise ValueError(f"duplicate runtime object {entry.id}")
        self._objects[entry.id] = entry
        if entry.parent_id:
            self._attachments.setdefault(entry.parent_id, []).append(entry.id)
        return entry

    def get(self, object_id: str) -> RuntimeObject:
        try:
            return self._objects[object_id]
        except KeyError as error:
            raise ValueError(f"unknown runtime object {object_id}") from error

    def children_of(self, object_id: str) -> list[RuntimeObject]:
        return [self.get(child_id) for child_id in self._attachments.get(object_id, [])]

    def all(self) -> dict[str, RuntimeObject]:
        return dict(self._objects)
