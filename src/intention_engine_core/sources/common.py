from __future__ import annotations

import datetime as dt
import json
import re
import socket
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Dict, List, Sequence, Tuple

from .base import SourceCandidate

USER_AGENT = "IntentionEngine/2.2"
DEFAULT_TIMEOUT = 10
_TRACKING_QUERY_KEYS = {
    "fbclid",
    "gclid",
    "mc_cid",
    "mc_eid",
    "ref",
    "ref_src",
    "utm_campaign",
    "utm_content",
    "utm_medium",
    "utm_source",
    "utm_term",
}


class SourceFetchException(RuntimeError):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code
        self.message = message


def utc_now() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


def parse_datetime(value: str) -> dt.datetime:
    if not value:
        return utc_now()
    normalized = value.strip().replace("Z", "+00:00")
    for date_format in (
        "%a, %d %b %Y %H:%M:%S %z",
        "%a, %d %b %Y %H:%M:%S %Z",
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d",
    ):
        try:
            parsed = dt.datetime.strptime(normalized, date_format)
            if parsed.tzinfo is None:
                return parsed.replace(tzinfo=dt.timezone.utc)
            return parsed.astimezone(dt.timezone.utc)
        except ValueError:
            continue
    try:
        parsed = dt.datetime.fromisoformat(normalized)
    except ValueError:
        return utc_now()
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=dt.timezone.utc)
    return parsed.astimezone(dt.timezone.utc)


def fetch_text(url: str, headers: Dict[str, str] | None = None, timeout: int = DEFAULT_TIMEOUT) -> str:
    req_headers = {"User-Agent": USER_AGENT, "Accept": "*/*"}
    if headers:
        req_headers.update(headers)
    request = urllib.request.Request(url, headers=req_headers)
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as exc:
        if exc.code == 429:
            raise SourceFetchException("source_rate_limited", f"HTTP 429 from {url}") from exc
        raise SourceFetchException("source_unknown", f"HTTP {exc.code} from {url}") from exc
    except (urllib.error.URLError, socket.timeout, TimeoutError) as exc:
        raise SourceFetchException("source_timeout", f"Timeout/network error for {url}: {exc}") from exc


def fetch_json(url: str, headers: Dict[str, str] | None = None, timeout: int = DEFAULT_TIMEOUT) -> Any:
    text = fetch_text(url, headers=headers, timeout=timeout)
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise SourceFetchException("source_parse_error", f"Invalid JSON from {url}") from exc


def normalize_url(raw_url: str) -> str:
    url = (raw_url or "").strip()
    if not url:
        return ""
    split = urllib.parse.urlsplit(url)

    if not split.scheme and split.netloc:
        split = urllib.parse.urlsplit(f"https:{url}")
    if not split.scheme and split.path.startswith("www."):
        split = urllib.parse.urlsplit(f"https://{url}")

    scheme = split.scheme.lower() if split.scheme else "https"
    hostname = (split.hostname or "").lower()
    port = split.port
    if port and ((scheme == "http" and port != 80) or (scheme == "https" and port != 443)):
        netloc = f"{hostname}:{port}"
    else:
        netloc = hostname

    path = re.sub(r"/+", "/", split.path or "/")
    if path != "/" and path.endswith("/"):
        path = path[:-1]

    query_pairs = urllib.parse.parse_qsl(split.query, keep_blank_values=True)
    cleaned_pairs = [
        (key, value)
        for key, value in query_pairs
        if key.lower() not in _TRACKING_QUERY_KEYS and not key.lower().startswith("utm_")
    ]
    cleaned_pairs.sort()
    query = urllib.parse.urlencode(cleaned_pairs)

    normalized = urllib.parse.urlunsplit((scheme, netloc, path, query, ""))
    return normalized if netloc else url


def title_fingerprint(title: str) -> str:
    terms = re.findall(r"[a-z0-9]{3,}", (title or "").lower())
    if not terms:
        return "untitled"
    unique = sorted(set(terms))
    return "-".join(unique[:14])


def make_candidate(
    *,
    source_label: str,
    source_id: str,
    source_name: str,
    source_type: str,
    source_index: int,
    title: str,
    url: str,
    engagement: float,
    created_at: dt.datetime,
) -> SourceCandidate:
    canonical = normalize_url(url)
    return SourceCandidate(
        source=source_label,
        title=title.strip(),
        url=url.strip(),
        engagement=float(engagement),
        created_at=created_at.astimezone(dt.timezone.utc),
        source_id=source_id,
        source_name=source_name,
        source_type=source_type,
        source_index=source_index,
        canonical_url=canonical,
        title_fingerprint=title_fingerprint(title),
    )


def build_source_error(source: Dict[str, Any], code: str, message: str) -> Dict[str, Any]:
    return {
        "source_id": str(source.get("id", "unknown")),
        "source_name": str(source.get("name", source.get("id", "unknown"))),
        "source_type": str(source.get("type", "unknown")),
        "code": code,
        "message": message,
    }


def candidate_domain(candidate: SourceCandidate) -> str:
    resolved = candidate.canonical_url or candidate.url
    host = urllib.parse.urlsplit(resolved).hostname
    return (host or "").lower()


def apply_source_filters(
    candidates: Sequence[SourceCandidate],
    filters: Dict[str, Any] | None,
    now: dt.datetime,
) -> Tuple[List[SourceCandidate], Dict[str, int]]:
    filters = filters if isinstance(filters, dict) else {}
    min_engagement = float(filters.get("min_engagement", 0.0) or 0.0)
    max_age_hours = filters.get("max_age_hours")
    max_age = float(max_age_hours) if isinstance(max_age_hours, (int, float)) else None

    include_keywords = [str(v).lower() for v in filters.get("include_keywords", []) if str(v).strip()]
    exclude_keywords = [str(v).lower() for v in filters.get("exclude_keywords", []) if str(v).strip()]
    domain_allowlist = {str(v).lower() for v in filters.get("domain_allowlist", []) if str(v).strip()}
    domain_blocklist = {str(v).lower() for v in filters.get("domain_blocklist", []) if str(v).strip()}

    kept: List[SourceCandidate] = []
    stats = {
        "input": len(candidates),
        "kept": 0,
        "dropped_min_engagement": 0,
        "dropped_max_age": 0,
        "dropped_include_keywords": 0,
        "dropped_exclude_keywords": 0,
        "dropped_domain_allowlist": 0,
        "dropped_domain_blocklist": 0,
    }

    for candidate in candidates:
        if candidate.engagement < min_engagement:
            stats["dropped_min_engagement"] += 1
            continue

        if max_age is not None:
            age_hours = max((now - candidate.created_at).total_seconds() / 3600.0, 0.0)
            if age_hours > max_age:
                stats["dropped_max_age"] += 1
                continue

        haystack = f"{candidate.title} {candidate.url}".lower()
        if include_keywords and not any(term in haystack for term in include_keywords):
            stats["dropped_include_keywords"] += 1
            continue

        if exclude_keywords and any(term in haystack for term in exclude_keywords):
            stats["dropped_exclude_keywords"] += 1
            continue

        domain = candidate_domain(candidate)
        if domain_allowlist and domain not in domain_allowlist:
            stats["dropped_domain_allowlist"] += 1
            continue

        if domain_blocklist and domain in domain_blocklist:
            stats["dropped_domain_blocklist"] += 1
            continue

        kept.append(candidate)

    stats["kept"] = len(kept)
    return kept, stats


def dedupe_candidates(candidates: Sequence[SourceCandidate]) -> Tuple[List[SourceCandidate], Dict[str, int]]:
    seen_urls: set[str] = set()
    seen_fingerprints: set[str] = set()

    deduped: List[SourceCandidate] = []
    stats = {
        "input": len(candidates),
        "kept": 0,
        "dropped_canonical_url": 0,
        "dropped_title_fingerprint": 0,
    }

    for candidate in candidates:
        canonical = candidate.canonical_url.strip().lower()
        fingerprint = candidate.title_fingerprint.strip().lower()

        if canonical and canonical in seen_urls:
            stats["dropped_canonical_url"] += 1
            continue

        if fingerprint and fingerprint in seen_fingerprints:
            stats["dropped_title_fingerprint"] += 1
            continue

        if canonical:
            seen_urls.add(canonical)
        if fingerprint:
            seen_fingerprints.add(fingerprint)
        deduped.append(candidate)

    stats["kept"] = len(deduped)
    return deduped, stats
