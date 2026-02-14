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
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ScopeRequest:
    area: str
    capability: str
    source: str


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

## Diagrams (Mermaid inline) - exactly 2

### Diagram 1: Core Flow
```mermaid
flowchart TD
  A[Entry] --> B[Validation]
  B --> C[Core Logic]
  C --> D[Data / Side Effects]
  D --> E[Output]
```

### Diagram 2: Ecosystem / Dependencies
```mermaid
flowchart TD
  Actor[User / API / Cron] --> ThisScope[{capability}]
  ThisScope --> DataStore[(DB / Cache)]
  ThisScope --> External[External Systems]
  ThisScope --> OtherScopes[Other Scopes]
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

    for req in requests:
        area_dir = _resolve_area_dir(product_root, req.area)
        if not args.dry_run:
            area_dir.mkdir(parents=True, exist_ok=True)
        scope_path = area_dir / f"{_slug(req.capability)}.md"
        rel = scope_path.relative_to(repo_root).as_posix()
        existed_before = scope_path.exists()

        if existed_before and not args.force:
            skipped.append(
                {"scope": rel, "status": "exists", "source": req.source}
            )
            continue

        payload = _render_template(req.area, req.capability)
        if not args.dry_run:
            scope_path.write_text(payload, encoding="utf-8")

        rec = {
            "scope": rel,
            "status": "updated" if existed_before else "created",
            "source": req.source,
        }
        if rec["status"] == "updated":
            updated.append(rec)
        else:
            created.append(rec)

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
