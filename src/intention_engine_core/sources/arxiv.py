from __future__ import annotations

import datetime as dt
from typing import Any, Dict, List

from .base import SourceAdapter, SourceFetchResult
from .common import SourceFetchException, build_source_error, fetch_text, make_candidate, parse_datetime
from .rss import parse_feed_items

_DEFAULT_CATEGORIES = ["cs.AI", "cs.LG", "cs.CL", "cs.CV"]


class ArxivSourceAdapter(SourceAdapter):
    source_type = "arxiv"

    def fetch(self, source: Dict[str, Any], now: dt.datetime) -> SourceFetchResult:
        raw_categories = source.get("categories", _DEFAULT_CATEGORIES)
        categories = [str(item).strip() for item in raw_categories if str(item).strip()] if isinstance(raw_categories, list) else []
        if not categories:
            categories = list(_DEFAULT_CATEGORIES)

        limit = int(source.get("limit", 20) or 20)
        timeout = int(source.get("timeout_s", 10) or 10)
        source_id = str(source.get("id", "arxiv-default"))
        source_name = str(source.get("name", "arXiv"))
        source_index = int(source.get("_source_index", 0))

        all_candidates = []
        errors: List[Dict[str, Any]] = []

        for category in categories:
            feed_url = f"https://export.arxiv.org/rss/{category}"
            try:
                xml_text = fetch_text(feed_url, timeout=timeout)
                entries = parse_feed_items(xml_text)
            except SourceFetchException as exc:
                errors.append(build_source_error(source, exc.code, f"{category}: {exc.message}"))
                continue

            for entry in entries:
                title = str(entry.get("title", "")).strip()
                link = str(entry.get("link", "")).strip()
                if not title or not link:
                    continue
                published = parse_datetime(str(entry.get("published", "")))
                all_candidates.append(
                    make_candidate(
                        source_label=f"arxiv/{category}",
                        source_id=source_id,
                        source_name=source_name,
                        source_type=self.source_type,
                        source_index=source_index,
                        title=title,
                        url=link,
                        engagement=1.0,
                        created_at=published,
                    )
                )

        all_candidates.sort(key=lambda item: item.created_at, reverse=True)
        candidates = all_candidates[: max(limit, 0)]

        return SourceFetchResult(
            candidates=candidates,
            errors=errors,
            stats={
                "fetched": len(candidates),
                "source_type": self.source_type,
                "categories": categories,
                "error_count": len(errors),
            },
        )
