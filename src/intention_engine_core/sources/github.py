from __future__ import annotations

import datetime as dt
import urllib.parse
from typing import Any, Dict

from .base import SourceAdapter, SourceFetchResult
from .common import SourceFetchException, build_source_error, fetch_json, make_candidate, parse_datetime


class GitHubSourceAdapter(SourceAdapter):
    source_type = "github"

    def fetch(self, source: Dict[str, Any], now: dt.datetime) -> SourceFetchResult:
        query = str(source.get("query", "agentic ai")).strip() or "agentic ai"
        limit = int(source.get("limit", 10) or 10)
        timeout = int(source.get("timeout_s", 10) or 10)
        source_id = str(source.get("id", "github-search"))
        source_name = str(source.get("name", "GitHub Search"))
        source_index = int(source.get("_source_index", 0))

        encoded = urllib.parse.quote(query)
        url = f"https://api.github.com/search/repositories?q={encoded}&sort=stars&order=desc&per_page={limit}"

        try:
            payload = fetch_json(url, headers={"Accept": "application/vnd.github+json"}, timeout=timeout)
        except SourceFetchException as exc:
            return SourceFetchResult(errors=[build_source_error(source, exc.code, exc.message)], stats={"fetched": 0})

        items = payload.get("items", []) if isinstance(payload, dict) else []
        candidates = []
        for repo in items:
            if not isinstance(repo, dict):
                continue
            name = str(repo.get("full_name", "unknown"))
            description = str(repo.get("description") or "No description")
            title = f"{name}: {description}"
            updated_at = parse_datetime(str(repo.get("updated_at", "")))
            candidates.append(
                make_candidate(
                    source_label="github/search",
                    source_id=source_id,
                    source_name=source_name,
                    source_type=self.source_type,
                    source_index=source_index,
                    title=title,
                    url=str(repo.get("html_url") or "https://github.com"),
                    engagement=float(repo.get("stargazers_count", 0)),
                    created_at=updated_at if isinstance(updated_at, dt.datetime) else now,
                )
            )

        return SourceFetchResult(
            candidates=candidates,
            stats={"fetched": len(candidates), "source_type": self.source_type, "query": query},
        )
