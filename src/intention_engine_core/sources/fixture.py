from __future__ import annotations

import datetime as dt
from typing import Any, Dict

from .base import SourceAdapter, SourceFetchResult
from .common import make_candidate, parse_datetime


class FixtureSourceAdapter(SourceAdapter):
    source_type = "fixture"
    required_fields = ("items",)

    def fetch(self, source: Dict[str, Any], now: dt.datetime) -> SourceFetchResult:
        candidates = []
        items = source.get("items", [])
        source_id = str(source.get("id", "fixture"))
        source_name = str(source.get("name", source_id))
        source_index = int(source.get("_source_index", 0))

        for item in items if isinstance(items, list) else []:
            if not isinstance(item, dict):
                continue
            title = str(item.get("title", "")).strip()
            url = str(item.get("url", "")).strip()
            if not title or not url:
                continue
            created = parse_datetime(str(item.get("created_at", now.isoformat())))
            candidates.append(
                make_candidate(
                    source_label=source_name,
                    source_id=source_id,
                    source_name=source_name,
                    source_type=self.source_type,
                    source_index=source_index,
                    title=title,
                    url=url,
                    engagement=float(item.get("engagement", 1.0)),
                    created_at=created,
                )
            )

        return SourceFetchResult(
            candidates=candidates,
            stats={"fetched": len(candidates), "source_type": self.source_type},
        )
