from __future__ import annotations

import datetime as dt
import re
from typing import Any, Dict

from .base import SourceAdapter, SourceFetchResult
from .common import SourceFetchException, build_source_error, fetch_json, make_candidate

_AI_HINT_TERMS = {
    "agent",
    "agents",
    "ai",
    "llm",
    "model",
    "mcp",
    "automation",
    "workflow",
    "reasoning",
}


class HackerNewsSourceAdapter(SourceAdapter):
    source_type = "hackernews"

    def fetch(self, source: Dict[str, Any], now: dt.datetime) -> SourceFetchResult:
        limit = int(source.get("limit", 20) or 20)
        timeout = int(source.get("timeout_s", 10) or 10)
        story_set = str(source.get("story_set", "top")).strip().lower()
        source_id = str(source.get("id", f"hackernews-{story_set}"))
        source_name = str(source.get("name", "Hacker News"))
        source_index = int(source.get("_source_index", 0))

        endpoint = {
            "new": "newstories",
            "best": "beststories",
            "top": "topstories",
        }.get(story_set, "topstories")

        try:
            ids = fetch_json(f"https://hacker-news.firebaseio.com/v0/{endpoint}.json", timeout=timeout)
        except SourceFetchException as exc:
            return SourceFetchResult(errors=[build_source_error(source, exc.code, exc.message)], stats={"fetched": 0})

        candidates = []
        for item_id in ids[: max(limit * 3, 30)] if isinstance(ids, list) else []:
            try:
                item = fetch_json(f"https://hacker-news.firebaseio.com/v0/item/{item_id}.json", timeout=timeout)
            except SourceFetchException as exc:
                return SourceFetchResult(errors=[build_source_error(source, exc.code, exc.message)], stats={"fetched": 0})

            if not isinstance(item, dict) or item.get("type") != "story":
                continue
            title = str(item.get("title", "")).strip()
            if not title:
                continue

            title_words = set(re.findall(r"[a-zA-Z]{2,}", title.lower()))
            if not (title_words & _AI_HINT_TERMS):
                continue

            url = str(item.get("url") or f"https://news.ycombinator.com/item?id={item_id}")
            engagement = float(item.get("score", 0)) + float(item.get("descendants", 0))
            created = dt.datetime.fromtimestamp(float(item.get("time", 0)), tz=dt.timezone.utc)
            candidates.append(
                make_candidate(
                    source_label="hackernews",
                    source_id=source_id,
                    source_name=source_name,
                    source_type=self.source_type,
                    source_index=source_index,
                    title=title,
                    url=url,
                    engagement=engagement,
                    created_at=created,
                )
            )

            if len(candidates) >= limit:
                break

        return SourceFetchResult(
            candidates=candidates,
            stats={"fetched": len(candidates), "source_type": self.source_type, "story_set": endpoint},
        )
