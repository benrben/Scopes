#!/usr/bin/env python3
"""scope_skeleton_generator.py - Generate scope skeletons with fill guidance.

Purpose:
- Turn LLM-provided names into ready-to-fill Capability Scope files.
- Remove blank-page friction by generating every required section with
  concise instructions for what to fill next.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ScopeRequest:
    area: str
    capability: str
    source: str


_CODE_FILES_CACHE: list[str] | None = None


def _slug(text: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9 _-]+", "", text).strip()
    cleaned = re.sub(r"\s+", "-", cleaned)
    cleaned = re.sub(r"-{2,}", "-", cleaned)
    return cleaned or "Unnamed"


def _parse_item(item: str, source: str) -> ScopeRequest:
    raw = item.strip()
    if not raw:
        raise ValueError("empty item")

    # Supported formats:
    # - "Area: Capability"
    # - "Area/Capability"
    # - "Area > Capability"
    if ":" in raw:
        area, capability = [part.strip() for part in raw.split(":", 1)]
    elif "/" in raw:
        area, capability = [part.strip() for part in raw.split("/", 1)]
    elif ">" in raw:
        area, capability = [part.strip() for part in raw.split(">", 1)]
    else:
        raise ValueError(
            f"cannot parse '{raw}'. Use 'Area: Capability' or 'Area/Capability'."
        )

    if not area or not capability:
        raise ValueError(f"invalid item '{raw}'")
    return ScopeRequest(area=area, capability=capability, source=source)


def _parse_json_items(raw: str) -> list[ScopeRequest]:
    data = json.loads(raw)
    out: list[ScopeRequest] = []
    if isinstance(data, list):
        for idx, item in enumerate(data):
            src = f"json[{idx}]"
            if isinstance(item, str):
                out.append(_parse_item(item, src))
                continue
            if isinstance(item, dict):
                area = str(item.get("area", "")).strip()
                capability = str(
                    item.get("capability", item.get("name", item.get("title", "")))
                ).strip()
                if not area or not capability:
                    raise ValueError(
                        f"{src} must include area + capability/name/title"
                    )
                out.append(
                    ScopeRequest(area=area, capability=capability, source=src)
                )
                continue
            raise ValueError(f"{src} unsupported item type")
        return out
    raise ValueError("JSON input must be an array")


def _collect_requests(args: argparse.Namespace) -> list[ScopeRequest]:
    items: list[ScopeRequest] = []

    if args.area and args.capability:
        items.append(
            ScopeRequest(
                area=args.area.strip(),
                capability=args.capability.strip(),
                source="--area/--capability",
            )
        )

    for item in args.item:
        items.append(_parse_item(item, "--item"))

    if args.items_file:
        lines = Path(args.items_file).read_text(
            encoding="utf-8", errors="replace"
        ).splitlines()
        for line in lines:
            text = line.strip()
            if not text or text.startswith("#"):
                continue
            items.append(_parse_item(text, "--items-file"))

    if args.items_json:
        maybe_file = Path(args.items_json)
        raw = (
            maybe_file.read_text(encoding="utf-8", errors="replace")
            if maybe_file.exists()
            else args.items_json
        )
        items.extend(_parse_json_items(raw))

    if not items and not sys.stdin.isatty():
        for line in sys.stdin.read().splitlines():
            text = line.strip()
            if not text:
                continue
            items.append(_parse_item(text, "stdin"))

    if not items:
        raise ValueError("no scope names provided")

    # De-duplicate by normalized area/capability
    seen: set[tuple[str, str]] = set()
    out: list[ScopeRequest] = []
    for req in items:
        key = (req.area.lower().strip(), req.capability.lower().strip())
        if key in seen:
            continue
        seen.add(key)
        out.append(req)
    return out


def _resolve_area_dir(product_root: Path, area: str) -> Path:
    desired = _slug(area).lower()
    for child in product_root.iterdir() if product_root.exists() else []:
        if child.is_dir() and child.name.lower() == desired:
            return child
    return product_root / _slug(area)


def _scan_code_files(repo_root: Path) -> list[str]:
    """Return a repo-relative list of code files (best-effort, time-boxed)."""
    global _CODE_FILES_CACHE
    if _CODE_FILES_CACHE is not None:
        return _CODE_FILES_CACHE

    try:
        r = subprocess.run(
            [
                "find",
                ".",
                "(",
                "-name",
                "*.ts",
                "-o",
                "-name",
                "*.tsx",
                "-o",
                "-name",
                "*.js",
                "-o",
                "-name",
                "*.jsx",
                "-o",
                "-name",
                "*.py",
                "-o",
                "-name",
                "*.go",
                "-o",
                "-name",
                "*.rs",
                "-o",
                "-name",
                "*.java",
                "-o",
                "-name",
                "*.kt",
                "-o",
                "-name",
                "*.rb",
                ")",
                "-not",
                "-path",
                "*/node_modules/*",
                "-not",
                "-path",
                "*/.git/*",
                "-not",
                "-path",
                "*/Scopes/*",
                "-not",
                "-path",
                "*/vendor/*",
                "-not",
                "-path",
                "*/dist/*",
                "-not",
                "-path",
                "*/build/*",
                "-not",
                "-path",
                "*/.venv/*",
                "-not",
                "-path",
                "*/venv/*",
                "-not",
                "-path",
                "*/__pycache__/*",
            ],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            timeout=15,
        )
        files = [l.lstrip("./") for l in r.stdout.splitlines() if l.strip()]
    except Exception:
        files = []

    _CODE_FILES_CACHE = files
    return files


def _norm_match(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", text.lower())


def _tokenize(text: str) -> list[str]:
    return [t.lower() for t in re.findall(r"[A-Za-z0-9]+", text) if t]


_MICRO_STOPWORDS = {
    "a",
    "an",
    "and",
    "or",
    "the",
    "to",
    "of",
    "for",
    "with",
    "from",
    "in",
    "on",
    "at",
    "by",
    "into",
    "over",
    "under",
    "via",
    "src",
    "lib",
    "app",
    "pkg",
    "internal",
    "cmd",
    "api",
    "index",
    "main",
    "util",
    "utils",
    "helper",
    "helpers",
    "common",
    "shared",
    "test",
    "tests",
    "spec",
    "specs",
    "__tests__",
    "fixtures",
    "mock",
    "mocks",
}


def _infer_micro_scopes(
    *,
    area: str,
    capability: str,
    code_files: list[str],
    limit: int,
) -> list[str]:
    """Infer micro-scope names from file-path signals (best-effort, deterministic)."""
    if limit <= 0:
        return []

    area_key = _norm_match(area)
    cap_key = _norm_match(capability)
    area_tokens = set(_tokenize(area))
    cap_tokens = set(_tokenize(capability))
    excluded_tokens = area_tokens | cap_tokens | _MICRO_STOPWORDS

    candidates: list[str] = []
    for f in code_files:
        nf = _norm_match(f)
        if (area_key and area_key in nf) or (cap_key and cap_key in nf):
            candidates.append(f)
            if len(candidates) >= 500:
                break

    lower = [c.lower() for c in candidates]

    def _has_any(needles: list[str]) -> bool:
        return any(any(n in p for n in needles) for p in lower)

    scopes: list[str] = []

    # Always include a core slice. Everything else is conditional.
    scopes.append("Core Flow")

    if _has_any(["route", "router", "controller", "handler", "endpoint", "/api", "cmd", "cli"]):
        scopes.append("Entry Points")
    if _has_any(["validate", "validator", "schema", "guard", "middleware"]):
        scopes.append("Validation")
    if _has_any(["authorize", "authoriz", "permission", "permissions", "rbac", "role", "acl"]):
        scopes.append("Authorization")
    if _has_any(["session", "token", "jwt", "cookie"]):
        scopes.append("Session / Tokens")
    if _has_any(["config", "configs", "configuration", "settings", "env", "dotenv", "flag", "flags", "feature"]):
        scopes.append("Configuration / Flags")
    if _has_any(["cache", "cached", "caching", "redis", "memcached"]):
        scopes.append("Caching")
    if _has_any(["queue", "job", "jobs", "worker", "workers", "async", "cron", "schedule", "scheduler"]):
        scopes.append("Async Jobs")
    if _has_any(
        [
            "db",
            "repo",
            "repository",
            "model",
            "schema",
            "migration",
            "migrate",
            "sql",
            "store",
            "storage",
        ]
    ):
        scopes.append("Persistence")
    if _has_any(["client", "sdk", "http", "grpc", "webhook", "external", "vendor", "integrat"]):
        scopes.append("Integrations")
    if _has_any(["log", "logger", "logging", "metric", "metrics", "trace", "tracing", "telemetry", "sentry", "opentelemetry"]):
        scopes.append("Observability")
    if _has_any(["email", "emails", "sms", "push", "notification", "notifications"]):
        scopes.append("Notifications")
    if any(p.endswith(".tsx") for p in lower) or _has_any(
        ["ui", "component", "components", "page", "pages", "view", "views", "frontend"]
    ):
        scopes.append("UI Surface")
    if _has_any(["error", "errors", "exception", "retry", "backoff", "timeout"]):
        scopes.append("Failures")

    # Derive up to 3 additional micro-scopes from frequent tokens in candidate paths.
    counts: Counter[str] = Counter()
    for path in candidates:
        for tok in _tokenize(path):
            if tok in excluded_tokens:
                continue
            if tok.isdigit() or len(tok) < 4:
                continue
            counts[tok] += 1

    for tok, _cnt in counts.most_common():
        title = tok.replace("_", " ").replace("-", " ").title()
        if any(title.lower() == s.lower() for s in scopes):
            continue
        scopes.append(title)
        if len(scopes) >= limit:
            break

    # If inference found nothing (common in small repos), return a conservative default.
    if not candidates:
        scopes = [
            "Core Flow",
            "Entry Points",
            "Validation",
            "Authorization",
            "Configuration / Flags",
            "Persistence",
            "Integrations",
            "UI Surface",
            "Failures",
            "Observability",
        ]

    # Enforce limit and stable order while de-duping case-insensitively.
    seen: set[str] = set()
    out: list[str] = []
    for s in scopes:
        key = s.lower().strip()
        if key in seen:
            continue
        seen.add(key)
        out.append(s)
        if len(out) >= limit:
            break
    return out


def _render_template(area: str, capability: str) -> str:
    return f"""# {capability}

## Summary
Fill with 1-3 sentences describing current behavior only (no future plans).
- What this capability does today:
- Primary outcome:
- Boundaries (what is out of scope):

## Where to Start in Code
Fill with concrete entrypoints and evidence links.
- **Primary entrypoint(s)**: `[path:Lx-Ly](path#Lx-Ly)` - first place execution begins
- **Key orchestrator/service**: `[path:Lx-Ly](path#Lx-Ly)` - main coordination logic
- **Data layer / schema** (if applicable): `[path:Lx-Ly](path#Lx-Ly)`
- **UI surface** (if applicable): `[path:Lx-Ly](path#Lx-Ly)`

## Tech Stack & Skills (Evidence-backed)
List only tools actually used here.

### Libraries / Tools Used
- **<Library/Tool>**: what it does here
  - **Evidence**: `[path:Lx-Ly](path#Lx-Ly)`
  - **Docs**: <link> - why relevant

### How It’s Used (Integration Points)
- **<integration point>**: `[path:Lx-Ly](path#Lx-Ly)` - one-line description

### Skills You Need (Grounded in the above)
- **<Skill>**: tied to one integration/library above

### Why This (Only if explicitly documented)
- **Rationale**: <reason or `[Unknown]`>
  - **Evidence**: `[path:Lx-Ly](path#Lx-Ly)` (ADR/README/etc)

### References
- <external doc> - one-line relevance

## Users & Triggers
Who initiates this capability? (user action, API client, cron, system event)

## What Happens
Inputs -> processing -> outputs (high-level flow).

## Rules & Constraints
System-enforced validations/permissions/limits.
- **Rule**: <rule>
  - **Evidence**: `[path:Lx-Ly](path#Lx-Ly)`

## Edge Cases & Failure Outcomes
List error states, retries, fallbacks, and empty states.

## Use Cases
Provide 3-7 concrete current-state use cases.
- **Use case**: <short>
  - **Trigger**: <what starts it>
  - **Outcome**: <result>
  - **Evidence**: `[path:Lx-Ly](path#Lx-Ly)`

## UI Surface
Remove this section if backend-only.

### Page Identity
- **Route / Path**: `[path:Lx-Ly](path#Lx-Ly)`
- **User Intent**: <primary goal>

### UI Mock (Low-fidelity, Evidence-backed)
```
+------------------------------------------+
| Header (Evidence: [link])                |
+------------------------------------------+
| [ Input Field ] [ Button ]               |
| (Evidence: [link])                       |
+------------------------------------------+
```

### Interactions & State
- **Navigation**: `[path:Lx-Ly](path#Lx-Ly)` -> destination
- **Validation**: `[path:Lx-Ly](path#Lx-Ly)` -> rule
- **States**: loading/error/empty `[path:Lx-Ly](path#Lx-Ly)`

### Data Binding
- **Displayed Data**: `[path:Lx-Ly](path#Lx-Ly)`
- **Actions**: `[path:Lx-Ly](path#Lx-Ly)`

## Scope Navigation
- **Parent**: [<parent scope>](relative_path.md)
- **Children**:
  - [<child scope>](relative_path.md)

## Scope Network (Cross-links)
- **Depends on / Uses (Upstream)**
  - [Scope Name](path.md) - evidence: `[path:Lx-Ly](path#Lx-Ly)`
- **Used by / Downstream**
  - [Scope Name](path.md) - evidence: `[path:Lx-Ly](path#Lx-Ly)`
- **Shares Data / Topics**
  - [Scope Name](path.md) - evidence: `[path:Lx-Ly](path#Lx-Ly)`
- **Possible Relations (Low Confidence)**
  - [Scope Name](path.md) - why uncertain + expected proof location

## Diagrams (Mermaid inline)
Update diagrams based on evidence. Delete optional diagrams that don't apply. Never leave placeholders unchanged.

### Core Flow (High-Level)
```mermaid
flowchart TD
  A[Entry] --> B[Validation]
  B --> C[Core Logic]
  C --> D[Data / Side Effects]
  D --> E[Output]
```

### Dependencies / Boundaries
```mermaid
flowchart TD
  Actor[User / API / Cron] --> ThisScope["{capability}"]
  ThisScope --> DataStore[(DB / Cache)]
  ThisScope --> External[External Systems]
  ThisScope --> OtherScopes[Other Scopes]
```

### Happy Path Sequence (One End-to-End Trace)
```mermaid
sequenceDiagram
  participant Actor as Actor
  participant Entry as Entry Point
  participant Svc as Service / Use Case
  participant Data as DB / Cache / External
  Actor->>Entry: Trigger / request
  Entry->>Svc: Call w/ validated input
  Svc->>Data: Read/Write
  Data-->>Svc: Result
  Svc-->>Entry: Output
  Entry-->>Actor: Response / UI update
```

### State Model (Optional; Delete If Not Stateful)
```mermaid
stateDiagram-v2
  [*] --> Idle
  Idle --> Processing: trigger
  Processing --> Success: ok
  Processing --> Failed: error
  Success --> Idle
  Failed --> Idle
```

### Data Model (Optional; Delete If Not Applicable)
```mermaid
erDiagram
  ENTITY_A ||--o{{ ENTITY_B : relates_to
  ENTITY_A {{
    string id
  }}
  ENTITY_B {{
    string id
  }}
```

## Usage & Flow Traces
At least one end-to-end trace per major path.

| Step | Layer | Evidence Link | Description |
|------|-------|---------------|-------------|
| 1 | Entry | [path:Lx-Ly](path#Lx-Ly) | Trigger received |
| 2 | Validation | [path:Lx-Ly](path#Lx-Ly) | Validation/authorization |
| 3 | Logic | [path:Lx-Ly](path#Lx-Ly) | Core processing |
| 4 | Data | [path:Lx-Ly](path#Lx-Ly) | Storage/network side effects |
| 5 | Output | [path:Lx-Ly](path#Lx-Ly) | Response/UI update |

## Code Evidence (Consolidated)
| Evidence Link | What it proves |
|--------------|-----------------|
| [path:Lx-Ly](path#Lx-Ly) | <claim proven> |

## Deep Dives / Sub-capabilities
Merge tiny scopes here. Mini-format: Summary -> Trace -> Evidence.

## Confidence & Notes
- **Confidence**: High / Medium / Low
- **Notes**: ambiguity, missing links, or conflicts.
"""


def _render_overview_template(area: str, capability: str, micro_scopes: list[str]) -> str:
    cap_slug = _slug(capability)
    micro_lines = "\n".join(
        f"- [{capability}: {name}](./{cap_slug}/{_slug(name)}.md) — TODO"
        for name in micro_scopes
    )
    micro_block = micro_lines if micro_lines else "- (none)"
    micro_block_nested = "\n".join("  " + line for line in micro_block.splitlines())

    return f"""# {capability}

## Summary
Fill with 1-3 sentences describing current behavior only (no future plans).

## Where to Start in Code
Fill with concrete entrypoints and evidence links.
- **Primary entrypoint(s)**: `[path:Lx-Ly](path#Lx-Ly)`
- **Key orchestrator/service**: `[path:Lx-Ly](path#Lx-Ly)`
- **Core data model / schema** (if applicable): `[path:Lx-Ly](path#Lx-Ly)`
- **Primary UI surface** (if applicable): `[path:Lx-Ly](path#Lx-Ly)`

## Sub-Scopes (Smaller, Linked)
These files split the capability into smaller slices. Fill them first, then keep this file as the router.
{micro_block}

## What Happens (High-Level)
Inputs -> processing -> outputs.

## Diagrams (Mermaid)
Update diagrams based on evidence. Delete optional diagrams that don't apply. Never leave placeholders unchanged.

### Core Flow (High-Level)
```mermaid
flowchart TD
  A[Entry] --> B[Validation]
  B --> C[Core Logic]
  C --> D[Data / Side Effects]
  D --> E[Output]
```

### Dependencies / Boundaries
```mermaid
flowchart TD
  Actor[User / API / Cron] --> ThisScope["{capability} (Router)"]
  ThisScope --> DataStore[(DB / Cache)]
  ThisScope --> External[External Systems]
  ThisScope --> OtherScopes[Other Scopes]
```

### Happy Path Sequence (One End-to-End Trace)
```mermaid
sequenceDiagram
  participant Actor as Actor
  participant Entry as Entry Point
  participant Svc as Service / Use Case
  participant Data as DB / Cache / External
  Actor->>Entry: Trigger / request
  Entry->>Svc: Call w/ validated input
  Svc->>Data: Read/Write
  Data-->>Svc: Result
  Svc-->>Entry: Output
  Entry-->>Actor: Response / UI update
```

### State Model (Optional; Delete If Not Stateful)
```mermaid
stateDiagram-v2
  [*] --> Idle
  Idle --> Processing: trigger
  Processing --> Success: ok
  Processing --> Failed: error
  Success --> Idle
  Failed --> Idle
```

### Data Model (Optional; Delete If Not Applicable)
```mermaid
erDiagram
  ENTITY_A ||--o{{ ENTITY_B : relates_to
  ENTITY_A {{
    string id
  }}
  ENTITY_B {{
    string id
  }}
```

## Scope Network (Cross-links)
- **Children (micro scopes)**
{micro_block_nested}
- **Depends on / Uses (Upstream)**
  - [Scope Name](path.md) - evidence: `[path:Lx-Ly](path#Lx-Ly)`
- **Used by / Downstream**
  - [Scope Name](path.md) - evidence: `[path:Lx-Ly](path#Lx-Ly)`

## Confidence & Notes
- **Confidence**: High / Medium / Low
- **Notes**: ambiguity, missing links, or conflicts.
"""


def _render_micro_template(
    *,
    area: str,
    capability: str,
    micro_name: str,
    siblings: list[str],
) -> str:
    cap_slug = _slug(capability)
    sibling_lines = "\n".join(
        f"  - [{capability}: {sib}](./{_slug(sib)}.md)"
        for sib in siblings
        if sib != micro_name
    ) or "  - (none)"

    return f"""# {capability}: {micro_name}

## Summary
Fill with 1-2 sentences describing the slice of behavior covered by this micro-scope.

## Where to Start in Code
Fill with concrete entrypoints and evidence links.
- **Primary entrypoint(s)**: `[path:Lx-Ly](path#Lx-Ly)`
- **Key file(s)**: `[path:Lx-Ly](path#Lx-Ly)`

## Diagrams (Mermaid)
Update diagrams based on evidence. Delete optional diagrams that don't apply. Never leave placeholders unchanged.

### Slice Flow
```mermaid
flowchart TD
  A[Entry] --> B[Validation]
  B --> C["Slice Logic"]
  C --> D["Data / Side Effects"]
  D --> E[Output]
```

### Slice Sequence (From One Real Trace)
```mermaid
sequenceDiagram
  participant Caller as Caller
  participant Entry as Entry Point
  participant Logic as Slice Logic
  participant Data as DB / Cache / External
  Caller->>Entry: Trigger / request
  Entry->>Logic: Call
  Logic->>Data: Read/Write
  Data-->>Logic: Result
  Logic-->>Entry: Output
  Entry-->>Caller: Response / UI update
```

### State Model (Optional; Delete If Not Stateful)
```mermaid
stateDiagram-v2
  [*] --> Idle
  Idle --> Running: trigger
  Running --> Done: ok
  Running --> Failed: error
  Done --> Idle
  Failed --> Idle
```

## Usage & Flow Traces
At least one end-to-end trace for this micro-scope.

| Step | Layer | Evidence Link | Description |
|------|-------|---------------|-------------|
| 1 | Entry | [path:Lx-Ly](path#Lx-Ly) | Trigger received |
| 2 | Validation | [path:Lx-Ly](path#Lx-Ly) | Validation/authorization |
| 3 | Logic | [path:Lx-Ly](path#Lx-Ly) | Core processing |
| 4 | Data | [path:Lx-Ly](path#Lx-Ly) | Storage/network side effects |
| 5 | Output | [path:Lx-Ly](path#Lx-Ly) | Response/UI update |

## Rules & Failure Outcomes
- **Rule / constraint**: <rule>
  - **Evidence**: `[path:Lx-Ly](path#Lx-Ly)`
- **Failure mode**: <failure>
  - **Evidence**: `[path:Lx-Ly](path#Lx-Ly)`

## Evidence Index
| Evidence Link | What it proves |
|--------------|-----------------|
| [path:Lx-Ly](path#Lx-Ly) | <claim proven> |

## Links
- **Parent**: [{capability}](../{cap_slug}.md)
- **Siblings**
{sibling_lines}

## Confidence & Notes
- **Confidence**: High / Medium / Low
- **Notes**: ambiguity, missing links, or conflicts.
"""


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate Scope skeleton files from LLM-provided names.",
        epilog=(
            "Examples:\n"
            "  scope_skeleton_generator.py --item 'Auth: Login'\n"
            "  scope_skeleton_generator.py --items-file ideas.txt\n"
            "  scope_skeleton_generator.py --items-json '[\"Billing: Refunds\"]'\n"
            "  cat names.txt | scope_skeleton_generator.py\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--repo-root", default=".", help="Repo root (default: .)")
    parser.add_argument("--area", default="", help="Single area name")
    parser.add_argument("--capability", default="", help="Single capability name")
    parser.add_argument(
        "--item",
        action="append",
        default=[],
        help="Scope item in format 'Area: Capability' (repeatable)",
    )
    parser.add_argument(
        "--items-file",
        default="",
        help="File with one scope item per line ('Area: Capability')",
    )
    parser.add_argument(
        "--items-json",
        default="",
        help="JSON array string/file of items (strings or {area, capability})",
    )
    parser.add_argument(
        "--micro",
        action="store_true",
        help="Generate an overview scope + multiple smaller micro-scopes per item.",
    )
    parser.add_argument(
        "--micro-scope",
        action="append",
        default=[],
        help="Micro-scope name to generate (repeatable). Implies --micro.",
    )
    parser.add_argument(
        "--micro-limit",
        type=int,
        default=12,
        help="Max micro-scopes per item when inferred (default: 12).",
    )
    parser.add_argument("--force", action="store_true", help="Overwrite existing files")
    parser.add_argument("--dry-run", action="store_true", help="Show actions without writing")
    parser.add_argument("--format", choices=["compact", "json"], default="compact")
    args = parser.parse_args()

    try:
        requests = _collect_requests(args)
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    repo_root = Path(args.repo_root).resolve()
    product_root = repo_root / "Scopes" / "Product"
    if not args.dry_run:
        product_root.mkdir(parents=True, exist_ok=True)

    created: list[dict[str, str]] = []
    updated: list[dict[str, str]] = []
    skipped: list[dict[str, str]] = []

    want_micro = bool(args.micro or args.micro_scope)
    code_files = _scan_code_files(repo_root) if want_micro else []

    for req in requests:
        area_dir = _resolve_area_dir(product_root, req.area)
        if not args.dry_run:
            area_dir.mkdir(parents=True, exist_ok=True)

        cap_slug = _slug(req.capability)

        if not want_micro:
            scope_path = area_dir / f"{cap_slug}.md"
            rel = scope_path.relative_to(repo_root).as_posix()
            existed_before = scope_path.exists()

            if existed_before and not args.force:
                skipped.append({"scope": rel, "status": "exists", "source": req.source, "kind": "macro"})
                continue

            payload = _render_template(req.area, req.capability)
            if not args.dry_run:
                scope_path.write_text(payload, encoding="utf-8")

            rec = {"scope": rel, "status": "updated" if existed_before else "created", "source": req.source, "kind": "macro"}
            (updated if existed_before else created).append(rec)
            continue

        micro_scopes = (
            [s.strip() for s in args.micro_scope if s.strip()]
            if args.micro_scope
            else _infer_micro_scopes(
                area=req.area,
                capability=req.capability,
                code_files=code_files,
                limit=args.micro_limit,
            )
        )

        # 1) Overview file (router)
        overview_path = area_dir / f"{cap_slug}.md"
        overview_rel = overview_path.relative_to(repo_root).as_posix()
        overview_existed = overview_path.exists()

        if overview_existed and not args.force:
            skipped.append({"scope": overview_rel, "status": "exists", "source": req.source, "kind": "overview"})
        else:
            payload = _render_overview_template(req.area, req.capability, micro_scopes)
            if not args.dry_run:
                overview_path.write_text(payload, encoding="utf-8")
            rec = {"scope": overview_rel, "status": "updated" if overview_existed else "created", "source": req.source, "kind": "overview"}
            (updated if overview_existed else created).append(rec)

        # 2) Micro scopes (children)
        micro_dir = area_dir / cap_slug
        if not args.dry_run:
            micro_dir.mkdir(parents=True, exist_ok=True)

        for name in micro_scopes:
            micro_path = micro_dir / f"{_slug(name)}.md"
            micro_rel = micro_path.relative_to(repo_root).as_posix()
            existed_before = micro_path.exists()

            if existed_before and not args.force:
                skipped.append({"scope": micro_rel, "status": "exists", "source": req.source, "kind": "micro"})
                continue

            payload = _render_micro_template(
                area=req.area,
                capability=req.capability,
                micro_name=name,
                siblings=micro_scopes,
            )
            if not args.dry_run:
                micro_path.write_text(payload, encoding="utf-8")

            rec = {"scope": micro_rel, "status": "updated" if existed_before else "created", "source": req.source, "kind": "micro", "group": overview_rel}
            (updated if existed_before else created).append(rec)

    if args.format == "json":
        print(
            json.dumps(
                {
                    "created": created,
                    "updated": updated,
                    "skipped": skipped,
                    "summary": {
                        "requested": len(requests),
                        "created": len(created),
                        "updated": len(updated),
                        "skipped": len(skipped),
                        "dry_run": args.dry_run,
                        "micro": want_micro,
                    },
                },
                indent=2,
            )
        )
        return 0

    print(
        f"Skeletons: requested={len(requests)} created={len(created)} "
        f"updated={len(updated)} skipped={len(skipped)}"
    )
    for item in created + updated + skipped:
        print(f"- {item['status']}: {item['scope']} (source={item['source']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
