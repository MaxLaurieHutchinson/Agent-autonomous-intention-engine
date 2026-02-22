#!/usr/bin/env python3
"""Intention Engine runtime.

Implements a deterministic, file-first autonomous loop:
- init runtime state
- run discovery + proposal routing
- generate daily brief
- show status

Designed for non-blocking background execution and safe state writes.
"""

from __future__ import annotations

import argparse
import contextlib
import dataclasses
import datetime as dt
import fcntl
import json
import math
import os
import re
import shutil
import tempfile
import textwrap
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

try:
    from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
except ImportError:  # pragma: no cover - Python <3.9 fallback
    ZoneInfo = None  # type: ignore[assignment]

    class ZoneInfoNotFoundError(Exception):
        pass


PROJECT = Path(__file__).resolve().parents[1]
WORKSPACE = Path(os.environ.get("INTENTION_ENGINE_WORKSPACE", str(PROJECT))).expanduser().resolve()
CONFIG_PATH = Path(os.environ.get("INTENTION_ENGINE_CONFIG", str(PROJECT / "config" / "runtime.json"))).expanduser().resolve()

_default_philosophy_in_workspace = WORKSPACE / "philosophy" / "PHILOSOPHY.md"
_default_philosophy_in_project = PROJECT / "philosophy" / "PHILOSOPHY.md"
PHILOSOPHY_SOURCE = Path(
    os.environ.get(
        "INTENTION_ENGINE_PHILOSOPHY_SOURCE",
        str(_default_philosophy_in_workspace if _default_philosophy_in_workspace.exists() else _default_philosophy_in_project),
    )
).expanduser().resolve()

MEMORY_DIR = WORKSPACE / "memory"
INTENT_PATH = MEMORY_DIR / "INTENT.md"
REFLECT_PATH = MEMORY_DIR / "REFLECT.md"
PHILOSOPHY_RUNTIME_PATH = MEMORY_DIR / "PHILOSOPHY.md"

PROPOSALS_DIR = MEMORY_DIR / "proposals"
INBOX_DIR = PROPOSALS_DIR / "inbox"
APPROVED_DIR = PROPOSALS_DIR / "approved"
REJECTED_DIR = PROPOSALS_DIR / "rejected"
DEFERRED_DIR = PROPOSALS_DIR / "deferred"

BRIEFINGS_DIR = MEMORY_DIR / "briefings"
METRICS_DIR = MEMORY_DIR / "metrics"
POLICIES_DIR = MEMORY_DIR / "policies"
TEMPLATES_DIR = MEMORY_DIR / "templates"

DATA_DIR = WORKSPACE / "data"
LAST_HUMAN_ACTIVITY_PATH = DATA_DIR / "last-human-activity.json"
BUDGET_STATE_PATH = DATA_DIR / "intention-engine-budget.json"
LOCK_PATH = METRICS_DIR / "intention-engine.lock"

USER_AGENT = "IntentionEngine/0.2 (+https://local.workspace)"
DEFAULT_TIMEOUT = 10

AI_HINT_TERMS = {
    "agent",
    "agents",
    "ai",
    "llm",
    "model",
    "mcp",
    "automation",
    "workflow",
    "reasoning",
    "openai",
    "anthropic",
    "gemini",
    "local",
    "inference",
}

LOW_SIGNAL_TITLE_TERMS = {
    "sports",
    "football",
    "hockey",
    "soccer",
    "basketball",
    "hydrogen",
    "car",
    "vehicle",
    "toyota",
    "politics",
}


@dataclasses.dataclass
class Candidate:
    source: str
    title: str
    url: str
    engagement: float
    created_at: dt.datetime


@dataclasses.dataclass
class ScoredCandidate:
    candidate: Candidate
    value: float
    urgency: float
    effort: float
    risk: float
    score: float
    autonomy_class: str
    external_sensitive: bool
    relevance: float


@dataclasses.dataclass
class Proposal:
    proposal_id: str
    title: str
    source: str
    url: str
    source_created_at: dt.datetime
    discovered_at: dt.datetime
    score: float
    relevance: float
    value: float
    urgency: float
    effort: float
    risk: float
    autonomy_class: str
    external_sensitive: bool
    saga_id: str
    chapter_id: str
    recommended_action: str
    narrative_reason: str
    evidence_target: str
    acceptance_test: str
    filepath: Path


def utc_now() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


def resolve_runtime_timezone(config: Dict[str, Any]) -> Tuple[dt.tzinfo, str]:
    tz_name = str(config.get("timezone", "UTC")).strip() or "UTC"
    if ZoneInfo is None:
        return dt.timezone.utc, "UTC"
    try:
        return ZoneInfo(tz_name), tz_name
    except ZoneInfoNotFoundError:
        return dt.timezone.utc, "UTC"


def runtime_date_key(config: Dict[str, Any], now: Optional[dt.datetime] = None) -> str:
    tz, _ = resolve_runtime_timezone(config)
    base = (now or utc_now()).astimezone(tz)
    return base.date().isoformat()


def read_text(path: Path, default: str = "") -> str:
    if not path.exists():
        return default
    return path.read_text(encoding="utf-8")


def read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return default


def atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", delete=False, encoding="utf-8", dir=str(path.parent)) as tmp:
        tmp.write(content)
        tmp_path = Path(tmp.name)
    tmp_path.replace(path)


def atomic_write_json(path: Path, payload: Any) -> None:
    atomic_write(path, json.dumps(payload, indent=2, sort_keys=True) + "\n")


@contextlib.contextmanager
def file_lock(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a+", encoding="utf-8") as f:
        fcntl.flock(f.fileno(), fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(f.fileno(), fcntl.LOCK_UN)


def clamp(value: float, lower: float, upper: float) -> float:
    return max(lower, min(upper, value))


def slugify(text: str, limit: int = 48) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", text.lower()).strip("-")
    return slug[:limit] or "proposal"


def parse_iso_or_epoch(value: Any) -> Optional[dt.datetime]:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        # Heuristic: milliseconds if too large.
        if value > 10_000_000_000:
            return dt.datetime.fromtimestamp(value / 1000.0, tz=dt.timezone.utc)
        return dt.datetime.fromtimestamp(value, tz=dt.timezone.utc)
    if isinstance(value, str):
        try:
            if value.endswith("Z"):
                value = value.replace("Z", "+00:00")
            parsed = dt.datetime.fromisoformat(value)
            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=dt.timezone.utc)
            return parsed.astimezone(dt.timezone.utc)
        except ValueError:
            return None
    return None


def load_config(path: Path) -> Dict[str, Any]:
    cfg = read_json(path, default={})
    if not cfg:
        raise RuntimeError(f"Missing config: {path}")
    return cfg


def ensure_runtime_structure(sync_philosophy: bool = False) -> Dict[str, Any]:
    created: List[str] = []

    for directory in [
        INBOX_DIR,
        APPROVED_DIR,
        REJECTED_DIR,
        DEFERRED_DIR,
        BRIEFINGS_DIR,
        METRICS_DIR,
        POLICIES_DIR,
        TEMPLATES_DIR,
        DATA_DIR,
    ]:
        if not directory.exists():
            directory.mkdir(parents=True, exist_ok=True)
            created.append(str(directory))

    if (not PHILOSOPHY_RUNTIME_PATH.exists()) or sync_philosophy:
        if not PHILOSOPHY_SOURCE.exists():
            raise RuntimeError(f"Missing philosophy source: {PHILOSOPHY_SOURCE}")
        shutil.copy2(PHILOSOPHY_SOURCE, PHILOSOPHY_RUNTIME_PATH)
        created.append(str(PHILOSOPHY_RUNTIME_PATH))

    if not REFLECT_PATH.exists():
        atomic_write(
            REFLECT_PATH,
            "# REFLECT.md - Intention Engine Session Reflections\n\n"
            "Append one section per autonomous run with results and learnings.\n",
        )
        created.append(str(REFLECT_PATH))

    if not BUDGET_STATE_PATH.exists():
        payload = {
            "date": utc_now().date().isoformat(),
            "daily_budget_gbp": 2.0,
            "reserve_budget_gbp": 0.2,
            "used_gbp": 0.0,
            "remaining_gbp": 1.8,
            "runs": [],
        }
        atomic_write_json(BUDGET_STATE_PATH, payload)
        created.append(str(BUDGET_STATE_PATH))

    fallback_policy = POLICIES_DIR / "fallbacks.md"
    if not fallback_policy.exists():
        atomic_write(
            fallback_policy,
            textwrap.dedent(
                """\
                # Fallback Policy

                ## Rules
                - If a workflow upgrade fails validation, revert to last known stable version.
                - Never apply fallback by deleting historical evidence.
                - Record fallback event in `memory/REFLECT.md` and metrics.

                ## Trigger Conditions
                - Runtime error in upgraded workflow
                - Validation hook fails
                - Budget overrun during upgraded execution
                """
            ),
        )
        created.append(str(fallback_policy))

    skill_evo_template = TEMPLATES_DIR / "proposal-skill-evolution.md"
    if not skill_evo_template.exists():
        atomic_write(
            skill_evo_template,
            textwrap.dedent(
                """\
                # Skill Evolution Proposal

                ## Context
                - Problem:
                - Why existing skills are insufficient:

                ## Proposed Skill Change
                - Skill:
                - Version:
                - Validation hook:
                - Fallback pointer:

                ## Risk and Cost
                - Risk class:
                - Estimated budget/time:

                ## Human Decision
                - [ ] Approve
                - [ ] Reject
                - [ ] Defer
                """
            ),
        )
        created.append(str(skill_evo_template))

    reflection_template = TEMPLATES_DIR / "reflection-multi-role.md"
    if not reflection_template.exists():
        atomic_write(
            reflection_template,
            textwrap.dedent(
                """\
                # Multi-Role Reflection Template

                ## Scout
                - What changed in the landscape?

                ## Builder
                - What was implemented?

                ## Critic
                - What risks or quality issues remain?

                ## Reflector
                - What should become durable knowledge?
                """
            ),
        )
        created.append(str(reflection_template))

    return {"created": created, "sync_philosophy": sync_philosophy}


def parse_last_human_activity() -> Optional[dt.datetime]:
    data = read_json(LAST_HUMAN_ACTIVITY_PATH, default={})
    if not data:
        return None
    for key in ("lastHumanMessageAt", "last_message_at", "timestamp"):
        if key in data:
            parsed = parse_iso_or_epoch(data[key])
            if parsed:
                return parsed
    return None


def minutes_since(timestamp: Optional[dt.datetime], now: Optional[dt.datetime] = None) -> Optional[float]:
    if timestamp is None:
        return None
    now = now or utc_now()
    delta = now - timestamp
    return delta.total_seconds() / 60.0


def load_budget_state(config: Dict[str, Any], now: Optional[dt.datetime] = None) -> Dict[str, Any]:
    default_daily = float(config.get("daily_budget_gbp", 2.0))
    default_reserve = float(config.get("reserve_budget_gbp", 0.2))
    default_remaining = max(default_daily - default_reserve, 0.0)
    today_key = runtime_date_key(config, now=now)

    state = read_json(
        BUDGET_STATE_PATH,
        default={
            "date": today_key,
            "daily_budget_gbp": default_daily,
            "reserve_budget_gbp": default_reserve,
            "used_gbp": 0.0,
            "remaining_gbp": default_remaining,
            "runs": [],
        },
    )

    if state.get("date") != today_key:
        state = {
            "date": today_key,
            "daily_budget_gbp": default_daily,
            "reserve_budget_gbp": default_reserve,
            "used_gbp": 0.0,
            "remaining_gbp": default_remaining,
            "runs": [],
        }

    # Reconcile config drift.
    state["daily_budget_gbp"] = default_daily
    state["reserve_budget_gbp"] = default_reserve
    if "remaining_gbp" not in state:
        state["remaining_gbp"] = max(default_daily - default_reserve - state.get("used_gbp", 0.0), 0.0)

    return state


def consume_budget(state: Dict[str, Any], mode: str, config: Dict[str, Any]) -> Tuple[bool, float, str]:
    mode_costs = config.get("mode_costs_gbp", {})
    cost = float(mode_costs.get(mode, 0.05))
    remaining = float(state.get("remaining_gbp", 0.0))
    if remaining < cost:
        return False, cost, "insufficient_budget"

    state["used_gbp"] = round(float(state.get("used_gbp", 0.0)) + cost, 4)
    state["remaining_gbp"] = round(remaining - cost, 4)
    return True, cost, "ok"


def fetch_json(url: str, headers: Optional[Dict[str, str]] = None, timeout: int = DEFAULT_TIMEOUT) -> Any:
    req_headers = {"User-Agent": USER_AGENT, "Accept": "application/json"}
    if headers:
        req_headers.update(headers)
    req = urllib.request.Request(url, headers=req_headers)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def fetch_reddit(subreddit: str, limit: int) -> List[Candidate]:
    urls = [
        f"https://www.reddit.com/r/{subreddit}/hot.json?limit={limit}&raw_json=1",
        f"https://old.reddit.com/r/{subreddit}/hot.json?limit={limit}&raw_json=1",
    ]
    payload = None
    last_exc: Optional[Exception] = None
    for url in urls:
        try:
            payload = fetch_json(url)
            break
        except Exception as exc:  # pragma: no cover - network best effort
            last_exc = exc
    if payload is None:
        raise RuntimeError(f"reddit fetch failed: {last_exc}")
    children = payload.get("data", {}).get("children", [])
    out: List[Candidate] = []
    for child in children:
        data = child.get("data", {})
        if data.get("stickied"):
            continue
        title = data.get("title")
        link = data.get("url")
        if not title or not link:
            continue
        engagement = float(data.get("ups", 0)) + float(data.get("num_comments", 0))
        created_ts = parse_iso_or_epoch(float(data.get("created_utc", 0))) or utc_now()
        out.append(
            Candidate(
                source=f"reddit/r/{subreddit}",
                title=title,
                url=link,
                engagement=engagement,
                created_at=created_ts,
            )
        )
    return out


def fetch_hackernews(limit: int) -> List[Candidate]:
    ids = fetch_json("https://hacker-news.firebaseio.com/v0/topstories.json")
    out: List[Candidate] = []
    for item_id in ids[: max(limit * 3, 30)]:
        item = fetch_json(f"https://hacker-news.firebaseio.com/v0/item/{item_id}.json")
        if item.get("type") != "story":
            continue
        title = item.get("title") or ""
        if not title:
            continue
        words = set(re.findall(r"[a-zA-Z]{2,}", title.lower()))
        if not (words & AI_HINT_TERMS):
            continue
        out.append(
            Candidate(
                source="hackernews",
                title=title,
                url=item.get("url") or f"https://news.ycombinator.com/item?id={item_id}",
                engagement=float(item.get("score", 0)) + float(item.get("descendants", 0)),
                created_at=parse_iso_or_epoch(float(item.get("time", 0))) or utc_now(),
            )
        )
        if len(out) >= limit:
            break
    return out


def fetch_github_repos(query: str, limit: int) -> List[Candidate]:
    q = urllib.parse.quote(query)
    url = f"https://api.github.com/search/repositories?q={q}&sort=stars&order=desc&per_page={limit}"
    payload = fetch_json(url, headers={"Accept": "application/vnd.github+json"})
    out: List[Candidate] = []
    for repo in payload.get("items", []):
        name = repo.get("full_name", "unknown")
        title = f"{name}: {repo.get('description') or 'No description'}"
        updated_at = parse_iso_or_epoch(repo.get("updated_at")) or utc_now()
        out.append(
            Candidate(
                source="github/search",
                title=title,
                url=repo.get("html_url") or "https://github.com",
                engagement=float(repo.get("stargazers_count", 0)),
                created_at=updated_at,
            )
        )
    return out


def discover_candidates(config: Dict[str, Any]) -> Tuple[List[Candidate], List[str]]:
    candidates: List[Candidate] = []
    errors: List[str] = []
    for source in config.get("sources", []):
        src_type = source.get("type")
        try:
            if src_type == "reddit":
                items = fetch_reddit(source["subreddit"], int(source.get("limit", 10)))
            elif src_type == "hackernews":
                items = fetch_hackernews(int(source.get("limit", 20)))
            elif src_type == "github":
                items = fetch_github_repos(source.get("query", "agentic ai"), int(source.get("limit", 10)))
            else:
                errors.append(f"unknown source type: {src_type}")
                continue
            candidates.extend(items)
        except Exception as exc:  # pragma: no cover - best effort network
            errors.append(f"{source.get('name', src_type)}: {exc}")
    return candidates, errors


def tokenize(text: str) -> List[str]:
    words = re.findall(r"[A-Za-z][A-Za-z0-9]{3,}", text.lower())
    stop = {
        "that",
        "this",
        "with",
        "from",
        "have",
        "been",
        "will",
        "what",
        "when",
        "where",
        "about",
        "your",
        "into",
        "they",
        "them",
        "were",
        "would",
        "there",
        "which",
        "while",
        "their",
    }
    return [w for w in words if w not in stop]


def extract_keywords(limit: int = 150) -> List[str]:
    intent_text = read_text(INTENT_PATH)
    philosophy_text = read_text(PHILOSOPHY_RUNTIME_PATH)
    combined = tokenize(intent_text + "\n" + philosophy_text)
    freq: Dict[str, int] = {}
    for word in combined:
        freq[word] = freq.get(word, 0) + 1
    ordered = sorted(freq.items(), key=lambda kv: kv[1], reverse=True)
    return [w for w, _ in ordered[:limit]]


def classify_risk(title: str, url: str, external_keywords: Iterable[str]) -> Tuple[float, bool, str]:
    haystack = f"{title} {url}".lower()
    external_sensitive = any(kw.lower() in haystack for kw in external_keywords)

    if external_sensitive:
        return 0.9, True, "human_gate"

    guarded_terms = ["integrate", "migration", "migrate", "replace", "security", "credential", "oauth", "auth"]
    if any(term in haystack for term in guarded_terms):
        return 0.55, False, "policy_guarded"

    return 0.25, False, "auto_safe"


def score_candidate(candidate: Candidate, keywords: List[str], config: Dict[str, Any]) -> ScoredCandidate:
    title_tokens = set(tokenize(candidate.title))
    keyword_set = set(keywords)
    overlap_count = len(title_tokens & keyword_set)
    relevance = clamp(overlap_count / max(8, len(title_tokens) + 1), 0.0, 1.0)

    title_words = set(re.findall(r"[a-zA-Z]{2,}", candidate.title.lower()))
    ai_signal = clamp(len(title_words & AI_HINT_TERMS) / 3.0, 0.0, 1.0)
    low_signal = 1.0 if (title_words & LOW_SIGNAL_TITLE_TERMS) else 0.0

    engagement_norm = clamp(math.log1p(max(candidate.engagement, 0.0)) / 8.0, 0.0, 1.0)
    value = clamp(
        (0.05 + (0.55 * relevance) + (0.20 * ai_signal) + (0.20 * engagement_norm)) - (0.25 * low_signal),
        0.01,
        1.0,
    )

    age_hours = max((utc_now() - candidate.created_at).total_seconds() / 3600.0, 0.0)
    urgency = clamp(1.0 - min(age_hours, 96.0) / 96.0, 0.1, 1.0)

    effort = 0.75
    title_lc = candidate.title.lower()
    if any(term in title_lc for term in ["framework", "migration", "benchmark", "architecture", "protocol"]):
        effort = 0.95
    if any(term in title_lc for term in ["deep", "survey", "comprehensive"]):
        effort = 1.1

    risk, external_sensitive, autonomy_class = classify_risk(
        candidate.title,
        candidate.url,
        config.get("external_action_keywords", []),
    )

    raw_score = (value * urgency) / (max(effort, 0.1) * max(risk, 0.15))
    score = clamp(raw_score * (0.25 + (0.75 * max(relevance, ai_signal))), 0.0, 2.0)

    return ScoredCandidate(
        candidate=candidate,
        value=value,
        urgency=urgency,
        effort=effort,
        risk=risk,
        score=score,
        autonomy_class=autonomy_class,
        external_sensitive=external_sensitive,
        relevance=relevance,
    )


def next_proposal_index(prefix_date: str) -> int:
    pattern = re.compile(rf"^P-{re.escape(prefix_date)}-(\d{{3}})")
    max_id = 0
    for directory in [INBOX_DIR, APPROVED_DIR, DEFERRED_DIR, REJECTED_DIR]:
        if not directory.exists():
            continue
        for path in directory.glob("*.md"):
            match = pattern.match(path.stem)
            if match:
                max_id = max(max_id, int(match.group(1)))
    return max_id + 1


def existing_proposal_slugs() -> set[str]:
    slugs: set[str] = set()
    pattern = re.compile(r"^P-\d{4}-\d{2}-\d{2}-\d{3}-(.+)$")
    for directory in [INBOX_DIR, APPROVED_DIR, DEFERRED_DIR, REJECTED_DIR]:
        if not directory.exists():
            continue
        for path in directory.glob("*.md"):
            match = pattern.match(path.stem)
            if match:
                slugs.add(match.group(1))
    return slugs


def proposal_markdown(proposal: Proposal) -> str:
    discovered_iso = proposal.discovered_at.isoformat()
    source_created_iso = proposal.source_created_at.isoformat()
    return textwrap.dedent(
        f"""\
        ---
        id: {proposal.proposal_id}
        title: {proposal.title}
        source: {proposal.source}
        url: {proposal.url}
        created_at: {discovered_iso}
        discovered_at: {discovered_iso}
        source_created_at: {source_created_iso}
        saga_id: {proposal.saga_id}
        chapter_id: {proposal.chapter_id}
        alignment:
          philosophy: {proposal.relevance:.2f}
          active_intent: {proposal.relevance:.2f}
        impact_score: {proposal.value:.2f}
        risk_score: {proposal.risk:.2f}
        autonomy_class: {proposal.autonomy_class}
        recommended_action: {proposal.recommended_action}
        acceptance_test: {proposal.acceptance_test}
        narrative_reason: {proposal.narrative_reason}
        evidence_target: {proposal.evidence_target}
        ---

        # {proposal.title}

        ## Why It Matters
        {proposal.narrative_reason}

        ## Recommended Action
        {proposal.recommended_action}

        ## Evidence Target
        {proposal.evidence_target}

        ## Acceptance Test
        {proposal.acceptance_test}

        ## Scoring
        - score: {proposal.score:.3f}
        - value: {proposal.value:.3f}
        - urgency: {proposal.urgency:.3f}
        - effort: {proposal.effort:.3f}
        - risk: {proposal.risk:.3f}
        - autonomy_class: `{proposal.autonomy_class}`
        """
    )


def build_proposal(
    scored: ScoredCandidate,
    config: Dict[str, Any],
    proposal_id: str,
    discovered_at: dt.datetime,
) -> Proposal:
    saga_id = config.get("intake", {}).get("default_saga_id", "S02")
    chapter_id = config.get("intake", {}).get("default_chapter_id", "C06")

    title = scored.candidate.title.strip().replace("\n", " ")
    narrative_reason = (
        "Matches active Intention Engine goals for proactive discovery and narrative-driven execution. "
        f"Relevance score {scored.relevance:.2f} from current INTENT + PHILOSOPHY context."
    )
    recommended_action = (
        f"Run a 60-minute spike on '{title[:80]}', capture findings in memory/knowledge, "
        "and convert into one executable intention if value remains high."
    )
    evidence_target = "Published memo or implementation artifact linked in INTENT entry"
    acceptance_test = "Actionable summary includes fit, effort, risk, and next step recommendation"

    filename = f"{proposal_id}-{slugify(title)}.md"
    filepath = INBOX_DIR / filename

    return Proposal(
        proposal_id=proposal_id,
        title=title,
        source=scored.candidate.source,
        url=scored.candidate.url,
        source_created_at=scored.candidate.created_at,
        discovered_at=discovered_at,
        score=scored.score,
        relevance=scored.relevance,
        value=scored.value,
        urgency=scored.urgency,
        effort=scored.effort,
        risk=scored.risk,
        autonomy_class=scored.autonomy_class,
        external_sensitive=scored.external_sensitive,
        saga_id=saga_id,
        chapter_id=chapter_id,
        recommended_action=recommended_action,
        narrative_reason=narrative_reason,
        evidence_target=evidence_target,
        acceptance_test=acceptance_test,
        filepath=filepath,
    )


def route_proposal(proposal: Proposal, config: Dict[str, Any]) -> str:
    routing = config.get("routing", {})
    auto_safe_threshold = float(routing.get("auto_safe_threshold", 0.75))
    guarded_threshold = float(routing.get("policy_guarded_threshold", 0.70))
    defer_threshold = float(routing.get("defer_threshold", 0.45))
    min_relevance_threshold = float(routing.get("min_relevance_threshold", 0.08))
    allow_guarded_auto = bool(routing.get("allow_policy_guarded_auto", True))

    if proposal.relevance < min_relevance_threshold:
        return "deferred"

    if proposal.score < defer_threshold:
        return "deferred"

    if proposal.autonomy_class == "human_gate":
        return "inbox"

    if proposal.autonomy_class == "auto_safe" and proposal.score >= auto_safe_threshold:
        return "approved"

    if proposal.autonomy_class == "policy_guarded":
        if allow_guarded_auto and proposal.score >= guarded_threshold and not proposal.external_sensitive:
            return "approved"
        return "inbox"

    return "inbox"


def move_proposal(path: Path, destination_bucket: str) -> Path:
    destination_dir = {
        "approved": APPROVED_DIR,
        "inbox": INBOX_DIR,
        "rejected": REJECTED_DIR,
        "deferred": DEFERRED_DIR,
    }[destination_bucket]
    destination_dir.mkdir(parents=True, exist_ok=True)
    target = destination_dir / path.name
    if path.resolve() == target.resolve():
        return path
    shutil.move(str(path), str(target))
    return target


def next_intention_id(intent_text: str) -> int:
    ids = [int(m.group(1)) for m in re.finditer(r"\[I(\d+)\]", intent_text)]
    if not ids:
        return 1
    return max(ids) + 1


def ensure_generated_intake_section(intent_text: str, saga_id: str, chapter_id: str) -> str:
    marker = "## Autonomous Intake (Generated)"
    if marker in intent_text:
        return intent_text

    block = textwrap.dedent(
        f"""

        {marker}
        - Parent Saga: {saga_id}
        - Parent Chapter: {chapter_id}

        ### Intentions
        """
    )
    return intent_text.rstrip() + block + "\n"


def insert_intention_from_proposal(proposal: Proposal, config: Dict[str, Any]) -> Optional[str]:
    if not INTENT_PATH.exists():
        return None

    intent_text = read_text(INTENT_PATH)
    saga_id = config.get("intake", {}).get("default_saga_id", "S02")
    chapter_id = config.get("intake", {}).get("default_chapter_id", "C06")
    status = config.get("intake", {}).get("default_intent_status", "NEXT")

    if f"] {proposal.title}" in intent_text or proposal.proposal_id in intent_text:
        return None

    intent_text = ensure_generated_intake_section(intent_text, saga_id, chapter_id)
    new_id = next_intention_id(intent_text)

    entry = textwrap.dedent(
        f"""\
        - **[I{new_id:02d}]** [{status}] {proposal.title}
          - Source: {proposal.source}
          - Proposal: {proposal.proposal_id}
          - Narrative reason: {proposal.narrative_reason}
          - Evidence target: {proposal.evidence_target}
        """
    )

    marker = "## Autonomous Intake (Generated)"
    section_start = intent_text.find(marker)
    if section_start < 0:
        updated = intent_text.rstrip() + "\n" + entry
    else:
        # Append at end to keep logic deterministic and avoid fragile parsing.
        updated = intent_text.rstrip() + "\n" + entry + "\n"

    atomic_write(INTENT_PATH, updated)
    return f"I{new_id:02d}"


def append_reflect_entry(mode: str, run_summary: Dict[str, Any]) -> None:
    timestamp = utc_now().strftime("%Y-%m-%d %H:%M UTC")
    entry = textwrap.dedent(
        f"""\

        ## {timestamp} — Intention Engine {mode} run
        **What happened:**
        - candidates discovered: {run_summary.get('candidates_discovered', 0)}
        - proposals created: {run_summary.get('proposals_created', 0)}
        - approved: {run_summary.get('approved', 0)}
        - deferred: {run_summary.get('deferred', 0)}
        - awaiting human gate: {run_summary.get('awaiting_human_gate', 0)}

        **Budget:**
        - run cost: £{run_summary.get('run_cost_gbp', 0):.2f}
        - remaining: £{run_summary.get('budget_remaining_gbp', 0):.2f}

        **Notes:**
        - non-blocking mode: background-safe execution
        - network errors: {run_summary.get('network_errors', 0)}
        """
    )
    current = read_text(REFLECT_PATH)
    atomic_write(REFLECT_PATH, current.rstrip() + entry + "\n")


def update_metrics(run_summary: Dict[str, Any], date_key: Optional[str] = None) -> Path:
    date_key = date_key or utc_now().date().isoformat()
    metrics_path = METRICS_DIR / f"intention-engine-{date_key}.json"
    payload = read_json(metrics_path, default={"date": date_key, "runs": []})
    payload.setdefault("runs", []).append(run_summary)
    payload["total_runs"] = len(payload["runs"])
    payload["total_proposals"] = sum(r.get("proposals_created", 0) for r in payload["runs"])
    payload["total_approved"] = sum(r.get("approved", 0) for r in payload["runs"])
    payload["total_deferred"] = sum(r.get("deferred", 0) for r in payload["runs"])
    payload["total_human_gate"] = sum(r.get("awaiting_human_gate", 0) for r in payload["runs"])
    atomic_write_json(metrics_path, payload)
    return metrics_path


def run_engine(mode: str, force: bool, dry_run: bool) -> Dict[str, Any]:
    config = load_config(CONFIG_PATH)

    with file_lock(LOCK_PATH):
        ensure_runtime_structure(sync_philosophy=False)

        runtime_tz, runtime_tz_name = resolve_runtime_timezone(config)
        now = utc_now()
        runtime_now = now.astimezone(runtime_tz)
        runtime_date = runtime_now.date().isoformat()
        last_human = parse_last_human_activity()
        idle_minutes = minutes_since(last_human, now)

        idle_threshold = float(config.get("idle_threshold_minutes", 5))
        missing_signal_policy = str(config.get("micro_missing_activity_signal", "skip")).strip().lower()
        if mode == "micro" and not force:
            if idle_minutes is None:
                if missing_signal_policy != "run":
                    return {
                        "status": "skipped_missing_activity_signal",
                        "mode": mode,
                        "idle_minutes": None,
                        "idle_threshold_minutes": idle_threshold,
                        "missing_signal_policy": missing_signal_policy,
                        "message": (
                            "micro run skipped because data/last-human-activity.json is missing; "
                            "set micro_missing_activity_signal=run to override"
                        ),
                    }
            elif idle_minutes <= idle_threshold:
                return {
                    "status": "skipped_active_human",
                    "mode": mode,
                    "idle_minutes": round(idle_minutes, 2),
                    "idle_threshold_minutes": idle_threshold,
                    "message": "micro run skipped to avoid main-thread interference",
                }

        budget_state = load_budget_state(config, now=now)
        mode_cost = float(config.get("mode_costs_gbp", {}).get(mode, 0.05))
        run_cost = mode_cost
        if dry_run:
            if float(budget_state.get("remaining_gbp", 0.0)) < mode_cost:
                return {
                    "status": "budget_blocked",
                    "mode": mode,
                    "reason": "insufficient_budget",
                    "remaining_gbp": budget_state.get("remaining_gbp", 0.0),
                    "required_gbp": mode_cost,
                    "dry_run": True,
                }
        else:
            ok, _, budget_reason = consume_budget(budget_state, mode, config)
            if not ok:
                return {
                    "status": "budget_blocked",
                    "mode": mode,
                    "reason": budget_reason,
                    "remaining_gbp": budget_state.get("remaining_gbp", 0.0),
                    "required_gbp": mode_cost,
                }

        candidates, errors = discover_candidates(config)
        keywords = extract_keywords(limit=200)

        scored = [score_candidate(c, keywords, config) for c in candidates]
        scored.sort(key=lambda s: s.score, reverse=True)

        max_items = int(config.get("intake", {}).get(f"{mode}_max_items", 2 if mode == "micro" else 5))
        picked = scored[:max_items]

        proposal_index = next_proposal_index(runtime_date)
        existing_slugs = existing_proposal_slugs()
        run_seen_slugs: set[str] = set()

        proposals: List[Proposal] = []
        idx = proposal_index
        for item in picked:
            candidate_slug = slugify(item.candidate.title)
            if candidate_slug in existing_slugs or candidate_slug in run_seen_slugs:
                continue

            proposal_id = f"P-{runtime_date}-{idx:03d}"
            idx += 1
            proposal = build_proposal(item, config, proposal_id, discovered_at=now)
            proposals.append(proposal)
            run_seen_slugs.add(candidate_slug)

        created = 0
        approved = 0
        deferred = 0
        awaiting_human_gate = 0
        inserted_intentions = 0

        for proposal in proposals:
            markdown = proposal_markdown(proposal)
            if not dry_run:
                atomic_write(proposal.filepath, markdown)
            created += 1

            route = route_proposal(proposal, config)
            if route == "approved":
                approved += 1
            elif route == "deferred":
                deferred += 1
            else:
                awaiting_human_gate += 1

            if not dry_run:
                final_path = move_proposal(proposal.filepath, route)
                proposal.filepath = final_path

                if (
                    route == "approved"
                    and bool(config.get("intake", {}).get("auto_insert_intentions", True))
                ):
                    inserted = insert_intention_from_proposal(proposal, config)
                    if inserted:
                        inserted_intentions += 1

        run_summary = {
            "timestamp": now.isoformat(),
            "runtime_local_timestamp": runtime_now.isoformat(),
            "runtime_timezone": runtime_tz_name,
            "runtime_date": runtime_date,
            "mode": mode,
            "status": "ok",
            "dry_run": dry_run,
            "idle_minutes": None if idle_minutes is None else round(idle_minutes, 2),
            "candidates_discovered": len(candidates),
            "proposals_created": created,
            "approved": approved,
            "deferred": deferred,
            "awaiting_human_gate": awaiting_human_gate,
            "inserted_intentions": inserted_intentions,
            "network_errors": len(errors),
            "network_error_details": errors,
            "run_cost_gbp": round(run_cost, 4),
            "budget_remaining_gbp": round(float(budget_state.get("remaining_gbp", 0.0)), 4),
        }

        budget_state.setdefault("runs", []).append(
            {
                "timestamp": now.isoformat(),
                "runtime_local_timestamp": runtime_now.isoformat(),
                "mode": mode,
                "cost_gbp": round(run_cost, 4),
                "proposals_created": created,
                "approved": approved,
                "deferred": deferred,
                "awaiting_human_gate": awaiting_human_gate,
                "dry_run": dry_run,
            }
        )

        if not dry_run:
            atomic_write_json(BUDGET_STATE_PATH, budget_state)
            update_metrics(run_summary, date_key=runtime_date)
            append_reflect_entry(mode, run_summary)

        return run_summary


def list_recent_proposals(
    directory: Path,
    now: Optional[dt.datetime] = None,
    max_age_hours: int = 24,
) -> List[Tuple[Path, Dict[str, str]]]:
    now = now or utc_now()
    out: List[Tuple[Path, Dict[str, str]]] = []
    for path in sorted(directory.glob("*.md"), reverse=True):
        text = read_text(path)
        if not text.startswith("---"):
            continue
        end = text.find("\n---", 3)
        if end < 0:
            continue
        frontmatter = text[4:end].strip().splitlines()
        fields: Dict[str, str] = {}
        for line in frontmatter:
            if ":" not in line:
                continue
            key, value = line.split(":", 1)
            fields[key.strip()] = value.strip()

        created = parse_iso_or_epoch(fields.get("discovered_at"))
        if created is None:
            created = parse_iso_or_epoch(fields.get("created_at"))
        if created is None:
            created = parse_iso_or_epoch(fields.get("id", ""))
        if created is not None:
            age_h = (now - created).total_seconds() / 3600.0
            if age_h > max_age_hours:
                continue
        out.append((path, fields))
    return out


def generate_brief() -> Dict[str, Any]:
    config = load_config(CONFIG_PATH)
    ensure_runtime_structure(sync_philosophy=False)

    runtime_tz, runtime_tz_name = resolve_runtime_timezone(config)
    now = utc_now()
    runtime_now = now.astimezone(runtime_tz)

    approved = list_recent_proposals(APPROVED_DIR, now=now, max_age_hours=24)
    inbox = list_recent_proposals(INBOX_DIR, now=now, max_age_hours=24)
    deferred = list_recent_proposals(DEFERRED_DIR, now=now, max_age_hours=24)

    date_key = runtime_now.date().isoformat()
    brief_path = BRIEFINGS_DIR / f"{date_key}-intention-brief.md"

    lines = [
        f"# Intention Engine Brief — {date_key}",
        "",
        "## Summary",
        f"- Approved proposals (24h): {len(approved)}",
        f"- Awaiting human gate (24h): {len(inbox)}",
        f"- Deferred proposals (24h): {len(deferred)}",
        "",
    ]

    if approved:
        lines.extend(["## Top Approved", ""])
        for path, fields in approved[:5]:
            lines.append(f"- **{fields.get('id', path.stem)}** {fields.get('title', path.stem)}")
            lines.append(f"  - source: {fields.get('source', 'unknown')}")
            lines.append(f"  - action: {fields.get('recommended_action', 'n/a')}")
        lines.append("")

    if inbox:
        lines.extend(["## Needs Human Decision", ""])
        for path, fields in inbox[:5]:
            lines.append(f"- **{fields.get('id', path.stem)}** {fields.get('title', path.stem)}")
            lines.append(f"  - reason: autonomy_class={fields.get('autonomy_class', 'unknown')}")
        lines.append("")

    lines.extend(
        [
            "## Notes",
            "- Generated by Intention Engine `brief` command.",
            "- Non-blocking policy retained: background tasks never take conversation priority.",
            f"- Timezone: {runtime_tz_name}",
            "",
        ]
    )

    atomic_write(brief_path, "\n".join(lines))
    return {
        "status": "ok",
        "brief_path": str(brief_path),
        "approved_count": len(approved),
        "inbox_count": len(inbox),
        "deferred_count": len(deferred),
    }


def status() -> Dict[str, Any]:
    ensure_runtime_structure(sync_philosophy=False)
    budget_state = load_budget_state(load_config(CONFIG_PATH))
    return {
        "status": "ok",
        "budget": budget_state,
        "queue": {
            "inbox": len(list(INBOX_DIR.glob("*.md"))),
            "approved": len(list(APPROVED_DIR.glob("*.md"))),
            "deferred": len(list(DEFERRED_DIR.glob("*.md"))),
            "rejected": len(list(REJECTED_DIR.glob("*.md"))),
        },
        "last_human_activity": read_json(LAST_HUMAN_ACTIVITY_PATH, default={}),
    }


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Intention Engine runtime")
    sub = p.add_subparsers(dest="command", required=True)

    init_p = sub.add_parser("init", help="Initialize runtime directories and templates")
    init_p.add_argument("--sync-philosophy", action="store_true", help="Force-copy philosophy to memory/PHILOSOPHY.md")

    run_p = sub.add_parser("run", help="Run autonomous scout+route loop")
    run_p.add_argument("--mode", choices=["micro", "deep"], default="micro")
    run_p.add_argument("--force", action="store_true", help="Ignore idle gate for micro runs")
    run_p.add_argument("--dry-run", action="store_true", help="Do not write files")

    sub.add_parser("brief", help="Generate daily Intention Engine brief")
    sub.add_parser("status", help="Show runtime status")

    return p


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "init":
        result = ensure_runtime_structure(sync_philosophy=args.sync_philosophy)
    elif args.command == "run":
        result = run_engine(mode=args.mode, force=args.force, dry_run=args.dry_run)
    elif args.command == "brief":
        result = generate_brief()
    elif args.command == "status":
        result = status()
    else:
        parser.error("Unknown command")
        return 2

    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
