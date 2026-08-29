"""`receipts` — check an agent's execution trace against its own summary."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import __version__
from .actions import actions as build_actions
from .adapters import UnknownTraceFormat, load
from .detectors import run
from .detectors.base import Severity
from .html import write as write_html
from .render import render
from .report import build
from .requirements import BadRequirements, load as load_spec
from . import cloud
from .bundle import NoTraces, build_bundle, load_labels
from .serve import serve

_GATE_CHOICES = ("high", "medium", "low", "never")
EXIT_OK, EXIT_GATED, EXIT_ERROR = 0, 1, 2


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="receipts",
        description="Verify what a coding agent actually did, from its own execution trace.",
    )
    parser.add_argument(
        "trace",
        type=Path,
        help="NDJSON trace from `bob run --format stream-json`, or a directory of them",
    )
    parser.add_argument("--workspace", type=Path, default=None, help="repo the agent worked in")
    parser.add_argument(
        "--spec", type=Path, default=None, metavar="FILE",
        help="requirements JSON to hold the run to (see `bob run --mode requirements`)",
    )
    parser.add_argument("--json", action="store_true", help="emit the evidence bundle as JSON")
    parser.add_argument(
        "--html", type=Path, default=None, metavar="FILE",
        help="write a self-contained HTML evidence bundle (required for a directory)",
    )
    parser.add_argument(
        "--fail-on",
        choices=_GATE_CHOICES,
        default="high",
        help="exit non-zero at this severity or above (default: high)",
    )
    parser.add_argument(
        "--watch", action="store_true",
        help="with a directory, serve a live audit board that follows it",
    )
    parser.add_argument(
        "--port", type=int, default=7878, help="port for --watch (default: 7878)",
    )
    parser.add_argument(
        "--labels", type=Path, default=None, metavar="FILE",
        help="optional {name: label} JSON marking control runs in the index",
    )
    parser.add_argument("--version", action="version", version=f"receipts {__version__}")
    return parser


def _gated(findings, threshold: str) -> bool:
    if threshold == "never":
        return False
    limit = Severity(threshold).rank
    return any(f.severity.rank <= limit for f in findings)


def _build_bundle(args) -> int:
    """A directory of traces produces one page covering all of them."""
    try:
        labels = load_labels(args.labels) if args.labels else None
    except ValueError as exc:
        print(f"receipts: {exc}", file=sys.stderr)
        return EXIT_ERROR

    if args.watch:
        try:
            serve(args.trace, args.port, labels)
        except OSError as exc:
            print(f"receipts: could not start the board: {exc}", file=sys.stderr)
            return EXIT_ERROR
        return EXIT_OK

    if args.html is None:
        print(
            f"receipts: {args.trace} is a directory; pass --html FILE to write the report",
            file=sys.stderr,
        )
        return EXIT_ERROR
    try:
        page = build_bundle(args.trace, args.html, labels)
    except (NoTraces, ValueError, OSError) as exc:
        print(f"receipts: {exc}", file=sys.stderr)
        return EXIT_ERROR
    print(f"receipts: wrote {page}")
    return EXIT_OK


_SUBCOMMANDS = ("login", "logout", "whoami", "push")


def _run_subcommand(argv: list[str]) -> int:
    """`receipts login|logout|whoami|push` — connecting a machine to a workspace.

    Kept out of argparse so that `receipts <trace>` stays the primary form: the
    audit is the tool, and pushing it somewhere is an extra.
    """
    name, rest = argv[0], argv[1:]
    try:
        if name == "login":
            return cloud.login()
        if name == "logout":
            return cloud.logout()
        if name == "whoami":
            return cloud.whoami()

        if not rest:
            print("receipts push: needs a trace file", file=sys.stderr)
            return EXIT_ERROR
        trace_path = Path(rest[0])
        trace = load(trace_path)
        findings = run(trace, None, None)
        report = build(trace, build_actions(trace), findings)
        return cloud.push(report.as_dict(), trace_path.stem)
    except cloud.CloudError as exc:
        print(f"receipts: {exc}", file=sys.stderr)
        return EXIT_ERROR
    except (UnknownTraceFormat, ValueError, OSError) as exc:
        print(f"receipts: {exc}", file=sys.stderr)
        return EXIT_ERROR
    except KeyboardInterrupt:
        print("\nreceipts: cancelled", file=sys.stderr)
        return EXIT_ERROR


def main(argv: list[str] | None = None) -> int:
    raw = list(sys.argv[1:] if argv is None else argv)
    if raw and raw[0] in _SUBCOMMANDS:
        return _run_subcommand(raw)

    args = _parser().parse_args(argv)

    if args.trace.is_dir():
        return _build_bundle(args)

    if not args.trace.is_file():
        print(f"receipts: no such trace: {args.trace}", file=sys.stderr)
        return EXIT_ERROR

    try:
        trace = load(args.trace)
    except (UnknownTraceFormat, ValueError) as exc:
        print(f"receipts: {exc}", file=sys.stderr)
        return EXIT_ERROR

    try:
        spec = load_spec(args.spec) if args.spec else None
    except BadRequirements as exc:
        print(f"receipts: {exc}", file=sys.stderr)
        return EXIT_ERROR

    findings = run(trace, args.workspace, spec)
    report = build(trace, build_actions(trace), findings)

    if args.json:
        print(json.dumps(report.as_dict(), indent=2))
    else:
        print(render(report))

    if args.html is not None:
        try:
            args.html.parent.mkdir(parents=True, exist_ok=True)
            write_html(report, args.html)
        except OSError as exc:
            print(f"receipts: could not write {args.html}: {exc}", file=sys.stderr)
            return EXIT_ERROR
        if not args.json:
            print(f"  evidence bundle: {args.html}")

    return EXIT_GATED if _gated(findings, args.fail_on) else EXIT_OK


if __name__ == "__main__":
    raise SystemExit(main())
