from __future__ import annotations

import abc
import dataclasses
import datetime as dt
from typing import Any, Dict, List


@dataclasses.dataclass
class SourceCandidate:
    source: str
    title: str
    url: str
    engagement: float
    created_at: dt.datetime
    source_id: str
    source_name: str
    source_type: str
    source_index: int
    canonical_url: str
    title_fingerprint: str


@dataclasses.dataclass
class SourceFetchResult:
    candidates: List[SourceCandidate] = dataclasses.field(default_factory=list)
    errors: List[Dict[str, Any]] = dataclasses.field(default_factory=list)
    stats: Dict[str, Any] = dataclasses.field(default_factory=dict)


class SourceAdapter(abc.ABC):
    source_type: str = "unknown"
    required_fields: tuple[str, ...] = ()

    def validate(self, source: Dict[str, Any]) -> List[str]:
        errors: List[str] = []
        for key in self.required_fields:
            value = source.get(key)
            if value is None or (isinstance(value, str) and not value.strip()):
                errors.append(f"{self.source_type}.{key} is required")
        return errors

    @abc.abstractmethod
    def fetch(self, source: Dict[str, Any], now: dt.datetime) -> SourceFetchResult:
        raise NotImplementedError
