#!/usr/bin/env python3
"""Intention Engine runtime with subcommand CLI and deterministic replay bundles."""

from __future__ import annotations

import argparse
import contextlib
import dataclasses
import datetime as dt
import fcntl
import hashlib
import json
import math
import os
import re
import shutil
import sys
import tempfile
import textwrap
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

from .path_resolver import resolve_config_path, resolve_path_value

PROJECT_ROOT = Path(__file__).resolve().parents[2]
WORKSPACE_ROOT = PROJECT_ROOT
DEFAULT_CONFIG_PATH = PROJECT_ROOT / "config" / "runtime.json"
DEFAULT_SCHEMA_PATH = PROJECT_ROOT / "config" / "runtime.schema.json"
FALLBACK_PHILOSOPHY_SOURCE = PROJECT_ROOT / "philosophy" / "PHILOSOPHY.md"

USER_AGENT = "IntentionEngine/2.1"
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
}
LOW_SIGNAL_TITLE_TERMS = {
    "sports",
    "football",
    "hockey",
    "soccer",
    "basketball",
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
    created_at: dt.datetime
    score: float
    relevance: float
    autonomy_class: str
    filepath: Path


@dataclasses.dataclass
class RuntimePaths:
    intent_path: Path
    reflect_path: Path
    philosophy_path: Path
    philosophy_fallback_path: Path
    proposals_dir: Path
    inbox_dir: Path
    approved_dir: Path
    rejected_dir: Path
    deferred_dir: Path
    briefings_dir: Path
    metrics_dir: Path
    budget_state_path: Path
    lock_path: Path
    logs_path: Path
    replay_dir: Path
    cron_jobs_path: Path


def utc_now() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


def to_iso8601(value: dt.datetime) -> str:
    return value.astimezone(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def parse_datetime(value: str) -> dt.datetime:
    if not value:
        return utc_now()
    normalized = value.strip().replace("Z", "+00:00")
    try:
        parsed = dt.datetime.fromisoformat(normalized)
    except ValueError:
        return utc_now()
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=dt.timezone.utc)
    return parsed.astimezone(dt.timezone.utc)


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
    with path.open("a+", encoding="utf-8") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def write_jsonl(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, sort_keys=True) + "\n")


def clamp(value: float, lower: float, upper: float) -> float:
    return max(lower, min(upper, value))


def slugify(text: str, limit: int = 48) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", text.lower()).strip("-")
    return slug[:limit] or "proposal"


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
    return [word for word in words if word not in stop]


def config_hash(config: Dict[str, Any]) -> str:
    payload = json.dumps(config, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def load_runtime_config(config_path: Path) -> Tuple[Dict[str, Any], List[str]]:
    if not config_path.exists():
        return {}, [f"Missing config: {config_path}"]
    data = read_json(config_path, default={})
    if not isinstance(data, dict):
        return {}, [f"Invalid config JSON object: {config_path}"]
    return data, []


def validate_runtime_config(config: Dict[str, Any]) -> Tuple[List[str], List[str]]:
    errors: List[str] = []
    warnings: List[str] = []

    if not isinstance(config.get("mode_profiles"), dict):
        errors.append("mode_profiles must be an object")
    else:
        for mode in ("micro", "deep", "research_deep"):
            profile = config["mode_profiles"].get(mode)
            if not isinstance(profile, dict):
                errors.append(f"mode_profiles.{mode} must be an object")
                continue
            for key in ("enabled", "max_items", "max_run_cost", "validation", "delegation"):
                if key not in profile:
                    errors.append(f"mode_profiles.{mode}.{key} is required")
            if isinstance(profile.get("max_items"), (int, float)) and profile.get("max_items", 0) <= 0:
                errors.append(f"mode_profiles.{mode}.max_items must be > 0")

    routing = config.get("routing")
    if not isinstance(routing, dict):
        errors.append("routing must be an object")
    else:
        required_routing = (
            "auto_safe_threshold",
            "policy_guarded_threshold",
            "defer_threshold",
            "min_relevance_threshold",
            "allow_policy_guarded_auto",
            "guarded_keywords",
            "always_human_gate_keywords",
        )
        for key in required_routing:
            if key not in routing:
                errors.append(f"routing.{key} is required")

    if not isinstance(config.get("paths"), dict):
        errors.append("paths must be an object")

    if "sources" not in config:
        warnings.append("sources missing; discovery will produce no candidates")

    return errors, warnings


def resolve_runtime_paths(config: Dict[str, Any], workspace_root: Path, project_root: Path) -> RuntimePaths:
    paths_cfg = config.get("paths", {})

    def path_for(key: str, default_value: str) -> Path:
        return resolve_path_value(str(paths_cfg.get(key, default_value)), workspace_root)

    proposals_dir = path_for("proposals_dir", "memory/proposals")
    metrics_dir = path_for("metrics_dir", "memory/metrics")

    return RuntimePaths(
        intent_path=path_for("intent_path", "memory/INTENT.md"),
        reflect_path=path_for("reflect_path", "memory/REFLECT.md"),
        philosophy_path=path_for("philosophy_path", "memory/PHILOSOPHY.md"),
        philosophy_fallback_path=path_for(
            "philosophy_fallback_path",
            str(project_root / "philosophy" / "PHILOSOPHY.md"),
        ),
        proposals_dir=proposals_dir,
        inbox_dir=proposals_dir / "inbox",
        approved_dir=proposals_dir / "approved",
        rejected_dir=proposals_dir / "rejected",
        deferred_dir=proposals_dir / "deferred",
        briefings_dir=path_for("briefings_dir", "memory/briefings"),
        metrics_dir=metrics_dir,
        budget_state_path=path_for("budget_state_path", "data/intention-engine-budget.json"),
        lock_path=path_for("lock_path", "memory/metrics/intention-engine.lock"),
        logs_path=path_for("logs_path", "logs/engine.jsonl"),
        replay_dir=path_for("replay_dir", "data/intention-engine-runs"),
        cron_jobs_path=path_for("cron_jobs_path", "~/.openclaw/cron/jobs.json"),
    )


def ensure_runtime_directories(paths: RuntimePaths) -> None:
    for directory in (
        paths.proposals_dir,
        paths.inbox_dir,
        paths.approved_dir,
        paths.rejected_dir,
        paths.deferred_dir,
        paths.metrics_dir,
        paths.briefings_dir,
        paths.replay_dir,
        paths.logs_path.parent,
        paths.lock_path.parent,
        paths.budget_state_path.parent,
    ):
        directory.mkdir(parents=True, exist_ok=True)


def fetch_json(url: str, headers: Optional[Dict[str, str]] = None, timeout: int = DEFAULT_TIMEOUT) -> Any:
    req_headers = {"User-Agent": USER_AGENT, "Accept": "application/json"}
    if headers:
        req_headers.update(headers)
    req = urllib.request.Request(url, headers=req_headers)
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def fetch_reddit(subreddit: str, limit: int) -> List[Candidate]:
    url = f"https://www.reddit.com/r/{subreddit}/hot.json?limit={limit}&raw_json=1"
    payload = fetch_json(url)
    children = payload.get("data", {}).get("children", [])
    output: List[Candidate] = []
    for child in children:
        data = child.get("data", {})
        if data.get("stickied"):
            continue
        title = data.get("title")
        link = data.get("url")
        if not title or not link:
            continue
        engagement = float(data.get("ups", 0)) + float(data.get("num_comments", 0))
        created_ts = dt.datetime.fromtimestamp(float(data.get("created_utc", 0)), tz=dt.timezone.utc)
        output.append(
            Candidate(
                source=f"reddit/r/{subreddit}",
                title=title,
                url=link,
                engagement=engagement,
                created_at=created_ts,
            )
        )
    return output


def fetch_hackernews(limit: int) -> List[Candidate]:
    ids = fetch_json("https://hacker-news.firebaseio.com/v0/topstories.json")
    output: List[Candidate] = []
    for item_id in ids[: max(limit * 3, 30)]:
        item = fetch_json(f"https://hacker-news.firebaseio.com/v0/item/{item_id}.json")
        if item.get("type") != "story":
            continue
        title = item.get("title") or ""
        if not title:
            continue
        title_words = set(re.findall(r"[a-zA-Z]{2,}", title.lower()))
        if not (title_words & AI_HINT_TERMS):
            continue
        engagement = float(item.get("score", 0)) + float(item.get("descendants", 0))
        created_ts = dt.datetime.fromtimestamp(float(item.get("time", 0)), tz=dt.timezone.utc)
        output.append(
            Candidate(
                source="hackernews",
                title=title,
                url=item.get("url") or f"https://news.ycombinator.com/item?id={item_id}",
                engagement=engagement,
                created_at=created_ts,
            )
        )
        if len(output) >= limit:
            break
    return output


def fetch_github_repos(query: str, limit: int) -> List[Candidate]:
    encoded_query = urllib.parse.quote(query)
    url = f"https://api.github.com/search/repositories?q={encoded_query}&sort=stars&order=desc&per_page={limit}"
    payload = fetch_json(url, headers={"Accept": "application/vnd.github+json"})
    output: List[Candidate] = []
    for repo in payload.get("items", []):
        name = repo.get("full_name", "unknown")
        title = f"{name}: {repo.get('description') or 'No description'}"
        updated_at = parse_datetime(str(repo.get("updated_at", "")))
        output.append(
            Candidate(
                source="github/search",
                title=title,
                url=repo.get("html_url") or "https://github.com",
                engagement=float(repo.get("stargazers_count", 0)),
                created_at=updated_at,
            )
        )
    return output


def load_fixture_candidates(source: Dict[str, Any]) -> List[Candidate]:
    output: List[Candidate] = []
    for item in source.get("items", []):
        title = str(item.get("title", "")).strip()
        url = str(item.get("url", "")).strip()
        if not title or not url:
            continue
        created = parse_datetime(str(item.get("created_at", to_iso8601(utc_now()))))
        output.append(
            Candidate(
                source=str(source.get("name", "fixture")),
                title=title,
                url=url,
                engagement=float(item.get("engagement", 1.0)),
                created_at=created,
            )
        )
    return output


def discover_candidates(config: Dict[str, Any]) -> Tuple[List[Candidate], List[str]]:
    candidates: List[Candidate] = []
    errors: List[str] = []

    for source in config.get("sources", []):
        source_type = source.get("type")
        try:
            if source_type == "reddit":
                items = fetch_reddit(str(source["subreddit"]), int(source.get("limit", 10)))
            elif source_type == "hackernews":
                items = fetch_hackernews(int(source.get("limit", 20)))
            elif source_type == "github":
                items = fetch_github_repos(str(source.get("query", "agentic ai")), int(source.get("limit", 10)))
            elif source_type == "fixture":
                items = load_fixture_candidates(source)
            else:
                errors.append(f"unknown source type: {source_type}")
                continue
            candidates.extend(items)
        except Exception as exc:  # pragma: no cover - external IO
            errors.append(f"{source.get('name', source_type)}: {exc}")

    return candidates, errors


def extract_keywords(paths: RuntimePaths, limit: int = 150) -> List[str]:
    intent_text = read_text(paths.intent_path)
    philosophy_text = read_text(paths.philosophy_path)
    if not philosophy_text:
        philosophy_text = read_text(paths.philosophy_fallback_path)

    combined = tokenize(intent_text + "\n" + philosophy_text)
    frequency: Dict[str, int] = {}
    for word in combined:
        frequency[word] = frequency.get(word, 0) + 1
    ordered = sorted(frequency.items(), key=lambda item: item[1], reverse=True)
    return [word for word, _ in ordered[:limit]]


def classify_risk(title: str, url: str, routing: Dict[str, Any]) -> Tuple[float, bool, str]:
    haystack = f"{title} {url}".lower()
    human_keywords = [str(term).lower() for term in routing.get("always_human_gate_keywords", [])]
    guarded_keywords = [str(term).lower() for term in routing.get("guarded_keywords", [])]

    if any(term and term in haystack for term in human_keywords):
        return 0.95, False, "human_gate"
    if any(term and term in haystack for term in guarded_keywords):
        return 0.55, False, "policy_guarded"
    return 0.25, False, "auto_safe"


def score_candidate(candidate: Candidate, keywords: List[str], routing: Dict[str, Any], now: dt.datetime) -> ScoredCandidate:
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

    age_hours = max((now - candidate.created_at).total_seconds() / 3600.0, 0.0)
    urgency = clamp(1.0 - min(age_hours, 96.0) / 96.0, 0.1, 1.0)

    effort = 0.75
    title_lc = candidate.title.lower()
    if any(term in title_lc for term in ["framework", "migration", "benchmark", "architecture", "protocol"]):
        effort = 0.95
    if any(term in title_lc for term in ["deep", "survey", "comprehensive"]):
        effort = 1.1

    risk, external_sensitive, autonomy_class = classify_risk(candidate.title, candidate.url, routing)
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


def route_from_values(score: float, relevance: float, autonomy_class: str, routing: Dict[str, Any]) -> str:
    min_relevance = float(routing.get("min_relevance_threshold", 0.08))
    defer_threshold = float(routing.get("defer_threshold", 0.45))
    auto_safe_threshold = float(routing.get("auto_safe_threshold", 0.75))
    policy_guarded_threshold = float(routing.get("policy_guarded_threshold", 0.70))
    allow_policy_guarded_auto = bool(routing.get("allow_policy_guarded_auto", False))

    if relevance < min_relevance:
        return "deferred"
    if score < defer_threshold:
        return "deferred"
    if autonomy_class == "human_gate":
        return "inbox"
    if autonomy_class == "auto_safe" and score >= auto_safe_threshold:
        return "approved"
    if autonomy_class == "policy_guarded" and score >= policy_guarded_threshold:
        return "approved" if allow_policy_guarded_auto else "inbox"
    return "inbox"


def route_candidate(scored: ScoredCandidate, routing: Dict[str, Any]) -> str:
    return route_from_values(scored.score, scored.relevance, scored.autonomy_class, routing)


def next_proposal_index(paths: RuntimePaths, prefix_date: str) -> int:
    pattern = re.compile(rf"^P-{re.escape(prefix_date)}-(\\d{{3}})")
    max_id = 0
    for directory in [paths.inbox_dir, paths.approved_dir, paths.deferred_dir, paths.rejected_dir]:
        if not directory.exists():
            continue
        for candidate in directory.glob("*.md"):
            match = pattern.match(candidate.stem)
            if match:
                max_id = max(max_id, int(match.group(1)))
    return max_id + 1


def existing_proposal_slugs(paths: RuntimePaths) -> set[str]:
    slugs: set[str] = set()
    pattern = re.compile(r"^P-\\d{4}-\\d{2}-\\d{2}-\\d{3}-(.+)$")
    for directory in [paths.inbox_dir, paths.approved_dir, paths.deferred_dir, paths.rejected_dir]:
        if not directory.exists():
            continue
        for candidate in directory.glob("*.md"):
            match = pattern.match(candidate.stem)
            if match:
                slugs.add(match.group(1))
    return slugs


def build_proposal(scored: ScoredCandidate, proposal_id: str, paths: RuntimePaths) -> Proposal:
    return Proposal(
        proposal_id=proposal_id,
        title=scored.candidate.title,
        source=scored.candidate.source,
        url=scored.candidate.url,
        created_at=scored.candidate.created_at,
        score=scored.score,
        relevance=scored.relevance,
        autonomy_class=scored.autonomy_class,
        filepath=paths.inbox_dir / f"{proposal_id}-{slugify(scored.candidate.title)}.md",
    )


def proposal_markdown(proposal: Proposal, scored: ScoredCandidate, route: str) -> str:
    return textwrap.dedent(
        f"""\
        ---
        id: {proposal.proposal_id}
        title: {proposal.title}
        source: {proposal.source}
        url: {proposal.url}
        created_at: {to_iso8601(proposal.created_at)}
        score: {proposal.score:.3f}
        relevance: {proposal.relevance:.2f}
        autonomy_class: {proposal.autonomy_class}
        routed_to: {route}
        ---

        # {proposal.title}

        ## Source
        {proposal.source}: {proposal.url}

        ## Scoring
        - score: {proposal.score:.3f}
        - relevance: {proposal.relevance:.3f}
        - value: {scored.value:.3f}
        - urgency: {scored.urgency:.3f}
        - effort: {scored.effort:.3f}
        - risk: {scored.risk:.3f}
        - autonomy_class: `{proposal.autonomy_class}`
        - routed_to: `{route}`
        """
    )


def move_proposal(path: Path, destination_bucket: str, paths: RuntimePaths) -> Path:
    destination_dir = {
        "approved": paths.approved_dir,
        "inbox": paths.inbox_dir,
        "rejected": paths.rejected_dir,
        "deferred": paths.deferred_dir,
    }[destination_bucket]
    destination_dir.mkdir(parents=True, exist_ok=True)
    target = destination_dir / path.name
    if path.resolve() == target.resolve():
        return path
    shutil.move(str(path), str(target))
    return target


def default_budget_state(config: Dict[str, Any], run_date: dt.date) -> Dict[str, Any]:
    daily_budget = float(config.get("daily_budget_gbp", 2.0))
    reserve_budget = float(config.get("reserve_budget_gbp", 0.2))
    return {
        "date": run_date.isoformat(),
        "daily_budget_gbp": daily_budget,
        "reserve_budget_gbp": reserve_budget,
        "used_gbp": 0.0,
        "remaining_gbp": max(daily_budget - reserve_budget, 0.0),
        "runs": [],
    }


def load_budget_state(paths: RuntimePaths, config: Dict[str, Any], run_date: dt.date) -> Dict[str, Any]:
    state = read_json(paths.budget_state_path, default_budget_state(config, run_date))
    if state.get("date") != run_date.isoformat():
        state = default_budget_state(config, run_date)
    return state


def consume_budget(state: Dict[str, Any], mode: str, profile: Dict[str, Any]) -> Tuple[bool, float, str]:
    cost = float(profile.get("max_run_cost", 0.0))
    remaining = float(state.get("remaining_gbp", 0.0))
    if remaining < cost:
        return False, cost, "insufficient_budget"
    state["used_gbp"] = round(float(state.get("used_gbp", 0.0)) + cost, 4)
    state["remaining_gbp"] = round(remaining - cost, 4)
    return True, cost, "ok"


def append_reflect_entry(paths: RuntimePaths, mode: str, run_summary: Dict[str, Any], run_started: dt.datetime) -> None:
    timestamp = run_started.strftime("%Y-%m-%d %H:%M UTC")
    entry = textwrap.dedent(
        f"""\

        ## {timestamp} - Intention Engine {mode} run
        - run id: {run_summary.get('run_id')}
        - candidates discovered: {run_summary.get('candidates_discovered', 0)}
        - proposals created: {run_summary.get('proposals_created', 0)}
        - approved: {run_summary.get('approved', 0)}
        - deferred: {run_summary.get('deferred', 0)}
        - awaiting human gate: {run_summary.get('awaiting_human_gate', 0)}
        - run cost: GBP {run_summary.get('run_cost_gbp', 0):.2f}
        - remaining budget: GBP {run_summary.get('budget_remaining_gbp', 0):.2f}
        """
    )
    current = read_text(paths.reflect_path)
    atomic_write(paths.reflect_path, current.rstrip() + entry + "\n")


def update_metrics(paths: RuntimePaths, run_summary: Dict[str, Any], run_started: dt.datetime) -> Path:
    date_key = run_started.date().isoformat()
    metrics_path = paths.metrics_dir / f"intention-engine-{date_key}.json"
    payload = read_json(metrics_path, default={"date": date_key, "runs": []})
    payload.setdefault("runs", []).append(run_summary)
    payload["total_runs"] = len(payload["runs"])
    payload["total_proposals"] = sum(run.get("proposals_created", 0) for run in payload["runs"])
    atomic_write_json(metrics_path, payload)
    return metrics_path


def write_engine_log(paths: RuntimePaths, level: str, event: str, message: str, extra: Optional[Dict[str, Any]] = None) -> None:
    payload: Dict[str, Any] = {
        "timestamp": to_iso8601(utc_now()),
        "level": level,
        "event": event,
        "message": message,
    }
    if extra:
        payload["extra"] = extra
    write_jsonl(paths.logs_path, payload)


def write_replay_bundle(
    paths: RuntimePaths,
    run_id: str,
    inputs_payload: Dict[str, Any],
    scores_payload: Dict[str, Any],
    decisions_payload: Dict[str, Any],
    config_digest: str,
) -> Path:
    run_dir = paths.replay_dir / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    atomic_write_json(run_dir / "inputs.json", inputs_payload)
    atomic_write_json(run_dir / "scores.json", scores_payload)
    atomic_write_json(run_dir / "decisions.json", decisions_payload)
    atomic_write(run_dir / "config-hash.txt", config_digest + "\n")
    return run_dir


def summarize_route_counts(routes: Iterable[str]) -> Tuple[int, int, int]:
    approved = 0
    deferred = 0
    awaiting_human_gate = 0
    for route in routes:
        if route == "approved":
            approved += 1
        elif route == "deferred":
            deferred += 1
        else:
            awaiting_human_gate += 1
    return approved, deferred, awaiting_human_gate


def run_engine(mode: str, config: Dict[str, Any], paths: RuntimePaths, dry_run: bool = False) -> Dict[str, Any]:
    run_started = utc_now()
    run_id = f"{run_started.strftime('%Y%m%dT%H%M%S%fZ')}-{mode}"

    mode_profiles = config.get("mode_profiles", {})
    profile = mode_profiles.get(mode)
    if not isinstance(profile, dict):
        return {"status": "invalid_mode", "mode": mode, "message": f"Mode profile missing: {mode}"}
    if not bool(profile.get("enabled", False)):
        return {"status": "mode_disabled", "mode": mode, "message": f"Mode '{mode}' is disabled"}

    routing = config.get("routing", {})

    with file_lock(paths.lock_path):
        ensure_runtime_directories(paths)

        budget_state = load_budget_state(paths, config, run_started.date())
        if dry_run:
            run_cost = 0.0
            budget_reason = "dry_run"
        else:
            ok, run_cost, budget_reason = consume_budget(budget_state, mode, profile)
            if not ok:
                return {
                    "status": "budget_blocked",
                    "mode": mode,
                    "reason": budget_reason,
                    "remaining_gbp": budget_state.get("remaining_gbp", 0.0),
                    "required_gbp": float(profile.get("max_run_cost", 0.0)),
                }

        candidates, discovery_errors = discover_candidates(config)
        keywords = extract_keywords(paths, limit=200)
        scored = [score_candidate(candidate, keywords, routing, run_started) for candidate in candidates]
        scored.sort(key=lambda item: item.score, reverse=True)

        max_items = int(profile.get("max_items", 1))
        picked = scored[:max_items]

        proposal_index = next_proposal_index(paths, run_started.date().isoformat())
        known_slugs = existing_proposal_slugs(paths)
        run_slugs: set[str] = set()

        decisions: List[Dict[str, Any]] = []
        proposals_to_write: List[Tuple[Proposal, ScoredCandidate, str]] = []

        index = proposal_index
        for scored_item in picked:
            candidate_slug = slugify(scored_item.candidate.title)
            if candidate_slug in known_slugs or candidate_slug in run_slugs:
                continue

            proposal_id = f"P-{run_started.date().isoformat()}-{index:03d}"
            index += 1
            proposal = build_proposal(scored_item, proposal_id, paths)
            route = route_candidate(scored_item, routing)
            proposals_to_write.append((proposal, scored_item, route))
            run_slugs.add(candidate_slug)

            decisions.append(
                {
                    "proposal_id": proposal.proposal_id,
                    "title": proposal.title,
                    "url": proposal.url,
                    "source": proposal.source,
                    "score": round(scored_item.score, 6),
                    "relevance": round(scored_item.relevance, 6),
                    "autonomy_class": scored_item.autonomy_class,
                    "route": route,
                }
            )

        approved, deferred, awaiting_human_gate = summarize_route_counts(item[2] for item in proposals_to_write)

        for proposal, scored_item, route in proposals_to_write:
            if dry_run:
                continue
            markdown = proposal_markdown(proposal, scored_item, route)
            atomic_write(proposal.filepath, markdown)
            proposal.filepath = move_proposal(proposal.filepath, route, paths)

        inputs_payload = {
            "run_id": run_id,
            "started_at": to_iso8601(run_started),
            "mode": mode,
            "dry_run": dry_run,
            "mode_profile": profile,
            "candidate_count": len(candidates),
            "candidates": [
                {
                    "source": candidate.source,
                    "title": candidate.title,
                    "url": candidate.url,
                    "engagement": round(candidate.engagement, 4),
                    "created_at": to_iso8601(candidate.created_at),
                }
                for candidate in candidates
            ],
            "discovery_errors": discovery_errors,
        }

        scores_payload = {
            "run_id": run_id,
            "keywords": keywords,
            "scores": [
                {
                    "title": scored_item.candidate.title,
                    "url": scored_item.candidate.url,
                    "source": scored_item.candidate.source,
                    "score": round(scored_item.score, 6),
                    "relevance": round(scored_item.relevance, 6),
                    "value": round(scored_item.value, 6),
                    "urgency": round(scored_item.urgency, 6),
                    "effort": round(scored_item.effort, 6),
                    "risk": round(scored_item.risk, 6),
                    "autonomy_class": scored_item.autonomy_class,
                }
                for scored_item in scored
            ],
        }

        decisions_payload = {
            "run_id": run_id,
            "started_at": to_iso8601(run_started),
            "mode": mode,
            "routing": routing,
            "decisions": decisions,
        }

        replay_dir = write_replay_bundle(
            paths=paths,
            run_id=run_id,
            inputs_payload=inputs_payload,
            scores_payload=scores_payload,
            decisions_payload=decisions_payload,
            config_digest=config_hash(config),
        )

        if not dry_run:
            budget_state.setdefault("runs", []).append(
                {
                    "timestamp": to_iso8601(run_started),
                    "mode": mode,
                    "run_id": run_id,
                    "cost_gbp": round(run_cost, 4),
                    "proposals_created": len(proposals_to_write),
                    "approved": approved,
                    "deferred": deferred,
                    "awaiting_human_gate": awaiting_human_gate,
                }
            )
            atomic_write_json(paths.budget_state_path, budget_state)

        run_summary = {
            "timestamp": to_iso8601(run_started),
            "run_id": run_id,
            "mode": mode,
            "status": "dry_run" if dry_run else "ok",
            "candidates_discovered": len(candidates),
            "proposals_created": len(proposals_to_write),
            "approved": approved,
            "deferred": deferred,
            "awaiting_human_gate": awaiting_human_gate,
            "network_errors": len(discovery_errors),
            "run_cost_gbp": round(run_cost, 4),
            "budget_remaining_gbp": round(float(budget_state.get("remaining_gbp", 0.0)), 4),
            "replay_bundle": str(replay_dir),
        }

        if discovery_errors:
            write_engine_log(
                paths,
                level="error",
                event="discovery_error",
                message="One or more discovery sources failed",
                extra={"errors": discovery_errors, "run_id": run_id},
            )

        if not dry_run:
            metrics_path = update_metrics(paths, run_summary, run_started)
            append_reflect_entry(paths, mode, run_summary, run_started)
            run_summary["metrics_path"] = str(metrics_path)

        write_engine_log(
            paths,
            level="info",
            event="run_complete",
            message=f"Run complete for mode={mode}",
            extra=run_summary,
        )

        return run_summary


def inspect_announce_failures(cron_jobs_path: Path) -> List[Dict[str, Any]]:
    payload = read_json(cron_jobs_path, default={})
    jobs = payload.get("jobs", []) if isinstance(payload, dict) else []
    failures: List[Dict[str, Any]] = []
    for job in jobs:
        state = job.get("state", {}) if isinstance(job, dict) else {}
        last_error = str(state.get("lastError", ""))
        if "announce delivery failed" not in last_error.lower():
            continue
        failures.append(
            {
                "id": job.get("id"),
                "name": job.get("name"),
                "last_error": last_error,
                "last_run_at_ms": state.get("lastRunAtMs"),
            }
        )
    return failures


def count_recent_log_errors(log_path: Path, now: dt.datetime) -> int:
    if not log_path.exists():
        return 0
    threshold = now - dt.timedelta(hours=24)
    count = 0
    for line in read_text(log_path).splitlines()[-500:]:
        if not line.strip():
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            continue
        if payload.get("level") not in {"error", "critical"}:
            continue
        timestamp = parse_datetime(str(payload.get("timestamp", "")))
        if timestamp >= threshold:
            count += 1
    return count


def status_report(config: Dict[str, Any], paths: RuntimePaths) -> Dict[str, Any]:
    now = utc_now()
    ensure_runtime_directories(paths)

    validation_errors, validation_warnings = validate_runtime_config(config)
    budget_state = load_budget_state(paths, config, now.date())

    queues = {
        "inbox": len(list(paths.inbox_dir.glob("*.md"))),
        "approved": len(list(paths.approved_dir.glob("*.md"))),
        "deferred": len(list(paths.deferred_dir.glob("*.md"))),
        "rejected": len(list(paths.rejected_dir.glob("*.md"))),
    }

    last_run = None
    if budget_state.get("runs"):
        last_run = budget_state["runs"][-1]

    announce_failures = inspect_announce_failures(paths.cron_jobs_path)
    recent_error_count = count_recent_log_errors(paths.logs_path, now)

    health_status = "ok"
    if validation_errors or announce_failures or recent_error_count > 0:
        health_status = "degraded"

    result = {
        "status": health_status,
        "timestamp": to_iso8601(now),
        "budget": {
            "date": budget_state.get("date"),
            "daily_budget_gbp": budget_state.get("daily_budget_gbp"),
            "reserve_budget_gbp": budget_state.get("reserve_budget_gbp"),
            "used_gbp": budget_state.get("used_gbp"),
            "remaining_gbp": budget_state.get("remaining_gbp"),
        },
        "queues": queues,
        "last_run": last_run,
        "health": {
            "config_valid": len(validation_errors) == 0,
            "validation_errors": validation_errors,
            "validation_warnings": validation_warnings,
            "announce_failures": announce_failures,
            "recent_log_errors_24h": recent_error_count,
        },
    }

    if announce_failures:
        write_engine_log(
            paths,
            level="warning",
            event="announce_delivery_failure",
            message="One or more orchestrated cron jobs report announce delivery failures",
            extra={"count": len(announce_failures), "jobs": announce_failures},
        )

    return result


def validate_runtime(config: Dict[str, Any], config_path: Path, paths: RuntimePaths) -> Dict[str, Any]:
    errors, warnings = validate_runtime_config(config)
    schema = read_json(DEFAULT_SCHEMA_PATH, default={})
    schema_available = bool(schema)

    path_checks = {
        "intent_path_exists": paths.intent_path.exists(),
        "philosophy_path_exists": paths.philosophy_path.exists() or paths.philosophy_fallback_path.exists(),
        "proposals_dir_exists": paths.proposals_dir.exists(),
    }

    for key, exists in path_checks.items():
        if not exists:
            warnings.append(f"{key} is false")

    return {
        "status": "ok" if not errors else "error",
        "config_path": str(config_path),
        "schema_path": str(DEFAULT_SCHEMA_PATH),
        "schema_loaded": schema_available,
        "errors": errors,
        "warnings": warnings,
        "paths": {
            "intent_path": str(paths.intent_path),
            "reflect_path": str(paths.reflect_path),
            "proposals_dir": str(paths.proposals_dir),
            "budget_state_path": str(paths.budget_state_path),
            "replay_dir": str(paths.replay_dir),
            "logs_path": str(paths.logs_path),
        },
    }


def replay_run(run_id: str, paths: RuntimePaths) -> Dict[str, Any]:
    replay_dir = paths.replay_dir / run_id
    decisions = read_json(replay_dir / "decisions.json", default={})
    scores = read_json(replay_dir / "scores.json", default={})
    inputs = read_json(replay_dir / "inputs.json", default={})

    if not decisions:
        return {
            "status": "error",
            "message": f"Replay bundle missing: {replay_dir}",
            "run_id": run_id,
        }

    routing = decisions.get("routing", {})
    mismatches: List[Dict[str, Any]] = []

    for item in decisions.get("decisions", []):
        expected = item.get("route")
        actual = route_from_values(
            score=float(item.get("score", 0.0)),
            relevance=float(item.get("relevance", 0.0)),
            autonomy_class=str(item.get("autonomy_class", "")),
            routing=routing,
        )
        if actual != expected:
            mismatches.append(
                {
                    "proposal_id": item.get("proposal_id"),
                    "title": item.get("title"),
                    "expected": expected,
                    "actual": actual,
                }
            )

    return {
        "status": "ok" if not mismatches else "error",
        "run_id": run_id,
        "bundle": str(replay_dir),
        "decision_count": len(decisions.get("decisions", [])),
        "mismatches": mismatches,
        "inputs_present": bool(inputs),
        "scores_present": bool(scores),
    }


def render_validate_text(payload: Dict[str, Any]) -> str:
    lines = [f"status: {payload['status']}", f"config: {payload['config_path']}"]
    if payload.get("errors"):
        lines.append("errors:")
        for entry in payload["errors"]:
            lines.append(f"- {entry}")
    if payload.get("warnings"):
        lines.append("warnings:")
        for entry in payload["warnings"]:
            lines.append(f"- {entry}")
    return "\n".join(lines)


def render_status_text(payload: Dict[str, Any]) -> str:
    health = payload.get("health", {})
    budget = payload.get("budget", {})
    queues = payload.get("queues", {})
    lines = [
        f"status: {payload.get('status')}",
        f"budget remaining: GBP {budget.get('remaining_gbp', 0):.2f}",
        f"queues: inbox={queues.get('inbox', 0)} approved={queues.get('approved', 0)} deferred={queues.get('deferred', 0)} rejected={queues.get('rejected', 0)}",
    ]
    if health.get("announce_failures"):
        lines.append(f"announce failures: {len(health['announce_failures'])}")
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Intention Engine runtime")
    parser.add_argument(
        "--config",
        default=os.environ.get("INTENTION_ENGINE_CONFIG", str(DEFAULT_CONFIG_PATH)),
        help="Path to runtime config JSON",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run", help="Execute an engine run")
    run_parser.add_argument("--mode", choices=["micro", "deep", "research_deep"], required=True)
    run_parser.add_argument("--dry-run", action="store_true", help="Do not mutate budget/proposals/metrics")

    status_parser = subparsers.add_parser("status", help="Show runtime status")
    status_parser.add_argument("--json", action="store_true", help="Emit JSON output")

    validate_parser = subparsers.add_parser("validate", help="Validate config and paths")
    validate_parser.add_argument("--json", action="store_true", help="Emit JSON output")

    replay_parser = subparsers.add_parser("replay", help="Replay a previous run bundle")
    replay_parser.add_argument("--run-id", required=True, help="Run ID to replay")

    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv if argv is not None else sys.argv[1:])

    config_path = resolve_config_path(str(args.config), DEFAULT_CONFIG_PATH, cwd=Path.cwd())
    config, load_errors = load_runtime_config(config_path)

    if load_errors:
        payload = {"status": "error", "errors": load_errors}
        print(json.dumps(payload, indent=2))
        return 1

    paths = resolve_runtime_paths(config, WORKSPACE_ROOT, PROJECT_ROOT)

    try:
        if args.command == "run":
            result = run_engine(args.mode, config, paths, dry_run=bool(args.dry_run))
            print(json.dumps(result, indent=2))
            return 0 if result.get("status") in {"ok", "dry_run"} else 1

        if args.command == "status":
            result = status_report(config, paths)
            if args.json:
                print(json.dumps(result, indent=2))
            else:
                print(render_status_text(result))
            return 0

        if args.command == "validate":
            result = validate_runtime(config, config_path, paths)
            if args.json:
                print(json.dumps(result, indent=2))
            else:
                print(render_validate_text(result))
            return 0 if result.get("status") == "ok" else 1

        if args.command == "replay":
            result = replay_run(args.run_id, paths)
            print(json.dumps(result, indent=2))
            return 0 if result.get("status") == "ok" else 1

        parser.error(f"Unknown command: {args.command}")
        return 2
    except Exception as exc:  # pragma: no cover - defensive boundary
        try:
            write_engine_log(
                paths,
                level="critical",
                event="unhandled_exception",
                message="Unhandled exception in intention engine runtime",
                extra={"error": str(exc), "command": args.command},
            )
        except Exception:
            pass
        print(json.dumps({"status": "error", "error": str(exc)}))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
