from __future__ import annotations

from typing import Dict, List

from .arxiv import ArxivSourceAdapter
from .base import SourceAdapter
from .fixture import FixtureSourceAdapter
from .github import GitHubSourceAdapter
from .hackernews import HackerNewsSourceAdapter
from .reddit import RedditSourceAdapter
from .rss import RSSSourceAdapter

_ADAPTERS: Dict[str, SourceAdapter] = {
    "reddit": RedditSourceAdapter(),
    "hackernews": HackerNewsSourceAdapter(),
    "github": GitHubSourceAdapter(),
    "fixture": FixtureSourceAdapter(),
    "rss": RSSSourceAdapter(),
    "arxiv": ArxivSourceAdapter(),
}


def supported_source_types() -> List[str]:
    return sorted(_ADAPTERS.keys())


def get_source_adapter(source_type: str) -> SourceAdapter | None:
    return _ADAPTERS.get(source_type)
