"""scopes/scripts/cmd_bridges.py — Script bridge commands: map, drift, validate, create, contract, trace, rename, move, hotspot."""
from __future__ import annotations

import sys

from cli_helpers import CliContext, _error


def cmd_map(ctx: CliContext, args) -> int:
    try:
        sys.path.insert(0, str(ctx.scripts_dir))
        from scope_map import main as scope_map_main  # type: ignore[import]

        map_args = [
            "--repo-root", str(ctx.project_root),
            "--format", args.format or "json",
        ]

        if hasattr(args, 'query') and args.query:
            map_args.extend(["--query", args.query])
        if hasattr(args, 'limit') and args.limit:
            map_args.extend(["--limit", str(args.limit)])
        if hasattr(args, 'area') and args.area:
            for area in (args.area if isinstance(args.area, list) else [args.area]):
                map_args.extend(["--area", area])
        if hasattr(args, 'depth') and args.depth:
            map_args.extend(["--depth", str(args.depth)])
        if hasattr(args, 'from_artifact') and args.from_artifact:
            map_args.extend(["--from-artifact", args.from_artifact])
        if hasattr(args, 'only') and args.only:
            map_args.extend(["--only", args.only])
        if hasattr(args, 'no_summary') and args.no_summary:
            map_args.append("--no-summary")
        if hasattr(args, 'no_evidence') and args.no_evidence:
            map_args.append("--no-evidence")
        if hasattr(args, 'scope') and args.scope:
            map_args.extend(["--scope", args.scope])

        sys.argv = ["scope_map.py"] + map_args
        return scope_map_main() or 0
    except SystemExit as e:
        return e.code if isinstance(e.code, int) else 1
    except Exception as e:
        print(_error(str(e)), file=sys.stderr)
        return 1


def cmd_drift(ctx: CliContext, args) -> int:
    try:
        sys.path.insert(0, str(ctx.scripts_dir))
        from drift_detector import main as drift_detector_main  # type: ignore[import]

        drift_args = [
            "--repo-root", str(ctx.project_root),
            "--format", args.format or "json",
        ]

        if hasattr(args, 'scope') and args.scope:
            drift_args.extend(["--scope", args.scope])
        if hasattr(args, 'area') and args.area:
            drift_args.extend(["--area", args.area])
        if hasattr(args, 'all') and args.all:
            drift_args.append("--all")
        if hasattr(args, 'stale_only') and args.stale_only:
            drift_args.append("--stale-only")
        if hasattr(args, 'days') and args.days:
            drift_args.extend(["--days", str(args.days)])
        if hasattr(args, 'limit') and args.limit:
            drift_args.extend(["--limit", str(args.limit)])

        sys.argv = ["drift_detector.py"] + drift_args
        return drift_detector_main() or 0
    except SystemExit as e:
        return e.code if isinstance(e.code, int) else 1
    except Exception as e:
        print(_error(str(e)), file=sys.stderr)
        return 1


def cmd_validate(ctx: CliContext, args) -> int:
    try:
        sys.path.insert(0, str(ctx.scripts_dir))
        from validate_scopes import main as validate_scopes_main  # type: ignore[import]

        validate_args = [
            "--repo-root", str(ctx.project_root),
            "--format", args.format or "json",
        ]

        if hasattr(args, 'scope') and args.scope:
            for scope in (args.scope if isinstance(args.scope, list) else [args.scope]):
                validate_args.extend(["--scope", scope])
        if hasattr(args, 'area') and args.area:
            validate_args.extend(["--area", args.area])
        if hasattr(args, 'all') and args.all:
            validate_args.append("--all")
        if hasattr(args, 'allow_stale') and args.allow_stale:
            validate_args.append("--allow-stale")

        sys.argv = ["validate_scopes.py"] + validate_args
        return validate_scopes_main() or 0
    except SystemExit as e:
        return e.code if isinstance(e.code, int) else 1
    except Exception as e:
        print(_error(str(e)), file=sys.stderr)
        return 1


def cmd_create(ctx: CliContext, args) -> int:
    try:
        sys.path.insert(0, str(ctx.scripts_dir))
        from scope_skeleton_generator import main as skeleton_main  # type: ignore[import]

        create_args = [
            "--repo-root", str(ctx.project_root),
            "--format", args.format or "json",
        ]

        if hasattr(args, 'scope') and args.scope:
            scope = args.scope.strip()
            if "/" in scope:
                area, capability = scope.split("/", 1)
                create_args.extend(["--area", area.strip()])
                create_args.extend(["--capability", capability.strip()])
            elif ":" in scope:
                area, capability = scope.split(":", 1)
                create_args.extend(["--area", area.strip()])
                create_args.extend(["--capability", capability.strip()])
            else:
                create_args.extend(["--area", scope])
        elif hasattr(args, 'area') and args.area:
            create_args.extend(["--area", args.area])
            if hasattr(args, 'capability') and args.capability:
                create_args.extend(["--capability", args.capability])

        if hasattr(args, 'item') and args.item:
            for item in (args.item if isinstance(args.item, list) else [args.item]):
                create_args.extend(["--item", item])
        if hasattr(args, 'items_file') and args.items_file:
            create_args.extend(["--items-file", args.items_file])
        if hasattr(args, 'items_json') and args.items_json:
            create_args.extend(["--items-json", args.items_json])
        if hasattr(args, 'micro') and args.micro:
            create_args.append("--micro")
        if hasattr(args, 'micro_scope') and args.micro_scope:
            for ms in (args.micro_scope if isinstance(args.micro_scope, list) else [args.micro_scope]):
                create_args.extend(["--micro-scope", ms])
        if hasattr(args, 'micro_limit') and args.micro_limit:
            create_args.extend(["--micro-limit", str(args.micro_limit)])
        if hasattr(args, 'force') and args.force:
            create_args.append("--force")
        if hasattr(args, 'dry_run') and args.dry_run:
            create_args.append("--dry-run")
        if hasattr(args, 'template') and args.template:
            create_args.extend(["--template", args.template])

        sys.argv = ["scope_skeleton_generator.py"] + create_args
        return skeleton_main() or 0
    except SystemExit as e:
        return e.code if isinstance(e.code, int) else 1
    except Exception as e:
        print(_error(str(e)), file=sys.stderr)
        return 1


def cmd_contract(ctx: CliContext, args) -> int:
    try:
        sys.path.insert(0, str(ctx.scripts_dir))
        from slice_contract_builder import main as contract_main  # type: ignore[import]

        contract_args = [
            "--repo-root", str(ctx.project_root),
        ]

        if hasattr(args, 'from_drift') and args.from_drift:
            contract_args.extend(["--from-drift", args.from_drift])
        if hasattr(args, 'from_skeletons') and args.from_skeletons:
            contract_args.extend(["--from-skeletons", args.from_skeletons])
        if hasattr(args, 'infer') and args.infer:
            contract_args.append("--infer")
        if hasattr(args, 'scope') and args.scope:
            contract_args.extend(["--scope", args.scope])
        if hasattr(args, 'target') and args.target:
            contract_args.extend(["--target", args.target])
        if hasattr(args, 'limit') and args.limit:
            contract_args.extend(["--limit", str(args.limit)])

        sys.argv = ["slice_contract_builder.py"] + contract_args
        return contract_main() or 0
    except SystemExit as e:
        return e.code if isinstance(e.code, int) else 1
    except Exception as e:
        print(_error(str(e)), file=sys.stderr)
        return 1


def cmd_trace(ctx: CliContext, args) -> int:
    try:
        sys.path.insert(0, str(ctx.scripts_dir))
        from scope_trace_stub_from_entrypoints import main as trace_main  # type: ignore[import]

        trace_args = [
            "--repo-root", str(ctx.project_root),
            "--format", args.format or "json",
        ]

        if hasattr(args, 'scope') and args.scope:
            for scope in (args.scope if isinstance(args.scope, list) else [args.scope]):
                trace_args.append(scope)
        if hasattr(args, 'desc') and args.desc:
            trace_args.extend(["--desc", args.desc])
        if hasattr(args, 'allow_missing_lines') and args.allow_missing_lines:
            trace_args.append("--allow-missing-lines")
        if hasattr(args, 'apply') and args.apply:
            trace_args.append("--apply")

        sys.argv = ["scope_trace_stub_from_entrypoints.py"] + trace_args
        return trace_main() or 0
    except SystemExit as e:
        return e.code if isinstance(e.code, int) else 1
    except Exception as e:
        print(_error(str(e)), file=sys.stderr)
        return 1


def cmd_rename(ctx: CliContext, args) -> int:
    try:
        sys.path.insert(0, str(ctx.scripts_dir))
        from scope_rename_guard import main as rename_main  # type: ignore[import]

        rename_args = [
            "--repo-root", str(ctx.project_root),
            "--format", args.format or "json",
        ]

        if hasattr(args, 'scope') and args.scope:
            rename_args.extend(["--scope", args.scope])
        if hasattr(args, 'to') and args.to:
            rename_args.extend(["--to", args.to])
        if hasattr(args, 'map') and args.map:
            rename_args.extend(["--map", args.map])
        if hasattr(args, 'apply') and args.apply:
            rename_args.append("--apply")
        if hasattr(args, 'dry_run') and args.dry_run:
            rename_args.append("--dry-run")
        if hasattr(args, 'update_plain') and args.update_plain:
            rename_args.append("--update-plain")
        if hasattr(args, 'strict') and args.strict:
            rename_args.append("--strict")

        sys.argv = ["scope_rename_guard.py"] + rename_args
        return rename_main() or 0
    except SystemExit as e:
        return e.code if isinstance(e.code, int) else 1
    except Exception as e:
        print(_error(str(e)), file=sys.stderr)
        return 1


def cmd_move(ctx: CliContext, args) -> int:
    return cmd_rename(ctx, args)


def cmd_hotspot(ctx: CliContext, args) -> int:
    try:
        sys.path.insert(0, str(ctx.scripts_dir))
        from hotspot_matrix import main as hotspot_main  # type: ignore[import]

        hotspot_args = [
            "--repo-root", str(ctx.project_root),
            "--format", args.format or "json",
        ]

        if hasattr(args, 'top') and args.top:
            hotspot_args.extend(["--top", str(args.top)])
        if hasattr(args, 'since_days') and args.since_days:
            hotspot_args.extend(["--since-days", str(args.since_days)])
        if hasattr(args, 'ext') and args.ext:
            for ext in (args.ext if isinstance(args.ext, list) else [args.ext]):
                hotspot_args.extend(["--ext", ext])
        if hasattr(args, 'exclude_dir') and args.exclude_dir:
            for exc in (args.exclude_dir if isinstance(args.exclude_dir, list) else [args.exclude_dir]):
                hotspot_args.extend(["--exclude-dir", exc])

        sys.argv = ["hotspot_matrix.py"] + hotspot_args
        return hotspot_main() or 0
    except SystemExit as e:
        return e.code if isinstance(e.code, int) else 1
    except Exception as e:
        print(_error(str(e)), file=sys.stderr)
        return 1
