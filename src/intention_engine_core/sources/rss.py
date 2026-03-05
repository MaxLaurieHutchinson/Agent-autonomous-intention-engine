from __future__ import annotations

import datetime as dt
import xml.etree.ElementTree as ET
from typing import Any, Dict, Iterable, List

from .base import SourceAdapter, SourceFetchResult
from .common import SourceFetchException, build_source_error, fetch_text, make_candidate, parse_datetime


def _strip(tag: str) -> str:
    return tag.split("}", 1)[-1] if "}" in tag else tag


def _child_text(element: ET.Element, names: Iterable[str]) -> str:
    wanted = set(names)
    for child in element:
        if _strip(child.tag) in wanted:
            return (child.text or "").strip()
    return ""


def _entry_link(entry: ET.Element) -> str:
    direct = _child_text(entry, ("link",))
    if direct:
        return direct
    for child in entry:
        if _strip(child.tag) != "link":
            continue
        href = child.attrib.get("href")
        rel = child.attrib.get("rel", "alternate")
        if href and rel in {"alternate", ""}:
            return href.strip()
    return ""


def parse_feed_items(xml_text: str) -> List[Dict[str, str]]:
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError as exc:
        raise SourceFetchException("source_parse_error", f"Invalid RSS/Atom feed: {exc}") from exc

    items: List[Dict[str, str]] = []

    tag = _strip(root.tag).lower()
    if tag == "rss":
        channel = root.find("channel")
        if channel is None:
            return items
        for item in channel.findall("item"):
            title = _child_text(item, ("title",))
            link = _entry_link(item)
            published = _child_text(item, ("pubDate", "published", "updated"))
            if title and link:
                items.append({"title": title, "link": link, "published": published})
        return items

    if tag == "feed":
        for entry in root.findall("{*}entry"):
            title = _child_text(entry, ("title",))
            link = _entry_link(entry)
            published = _child_text(entry, ("published", "updated"))
            if title and link:
                items.append({"title": title, "link": link, "published": published})
        return items

    return items


class RSSSourceAdapter(SourceAdapter):
    source_type = "rss"
    required_fields = ("feed_url",)

    def fetch(self, source: Dict[str, Any], now: dt.datetime) -> SourceFetchResult:
        feed_url = str(source.get("feed_url", "")).strip()
        limit = int(source.get("limit", 20) or 20)
        timeout = int(source.get("timeout_s", 10) or 10)
        source_id = str(source.get("id", "rss"))
        source_name = str(source.get("name", source_id))
        source_index = int(source.get("_source_index", 0))

        try:
            xml_text = fetch_text(feed_url, timeout=timeout)
            items = parse_feed_items(xml_text)
        except SourceFetchException as exc:
            return SourceFetchResult(errors=[build_source_error(source, exc.code, exc.message)], stats={"fetched": 0})

        candidates = []
        for item in items[: max(limit, 0)]:
            title = str(item.get("title", "")).strip()
            link = str(item.get("link", "")).strip()
            if not title or not link:
                continue
            published = parse_datetime(str(item.get("published", "")))
            candidates.append(
                make_candidate(
                    source_label=source_name,
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

        return SourceFetchResult(
            candidates=candidates,
            stats={"fetched": len(candidates), "source_type": self.source_type, "feed_url": feed_url},
        )
