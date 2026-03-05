from __future__ import annotations

import datetime as dt
from typing import Any, Dict

from .base import SourceAdapter, SourceFetchResult
from .common import SourceFetchException, build_source_error, fetch_json, make_candidate


class RedditSourceAdapter(SourceAdapter):
    source_type = "reddit"
    required_fields = ("subreddit",)

    def fetch(self, source: Dict[str, Any], now: dt.datetime) -> SourceFetchResult:
        subreddit = str(source.get("subreddit", "")).strip()
        limit = int(source.get("limit", 10) or 10)
        timeout = int(source.get("timeout_s", 10) or 10)
        source_id = str(source.get("id", f"reddit-{subreddit.lower()}"))
        source_name = str(source.get("name", f"reddit/{subreddit}"))
        source_index = int(source.get("_source_index", 0))

        url = f"https://www.reddit.com/r/{subreddit}/hot.json?limit={limit}&raw_json=1"
        try:
            payload = fetch_json(url, timeout=timeout)
        except SourceFetchException as exc:
            return SourceFetchResult(errors=[build_source_error(source, exc.code, exc.message)], stats={"fetched": 0})

        children = payload.get("data", {}).get("children", []) if isinstance(payload, dict) else []
        candidates = []
        for child in children:
            data = child.get("data", {}) if isinstance(child, dict) else {}
            if data.get("stickied"):
                continue
            title = str(data.get("title", "")).strip()
            link = str(data.get("url", "")).strip()
            if not title or not link:
                continue
            engagement = float(data.get("ups", 0)) + float(data.get("num_comments", 0))
            created_ts = dt.datetime.fromtimestamp(float(data.get("created_utc", 0)), tz=dt.timezone.utc)
            candidates.append(
                make_candidate(
                    source_label=f"reddit/r/{subreddit}",
                    source_id=source_id,
                    source_name=source_name,
                    source_type=self.source_type,
                    source_index=source_index,
                    title=title,
                    url=link,
                    engagement=engagement,
                    created_at=created_ts,
                )
            )
            if len(candidates) >= limit:
                break

        return SourceFetchResult(
            candidates=candidates,
            stats={"fetched": len(candidates), "source_type": self.source_type},
        )
