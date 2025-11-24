"""CLI wrapper around `src.cost_tracker.CostTracker` for logging API usage."""

from __future__ import annotations

import argparse
import sys
from typing import Tuple

from src.cost_tracker import CostTracker


def _parse_tokens_pair(raw: str) -> Tuple[int, int]:
    """Parse token pair in the form INPUT,OUTPUT."""
    parts = [p.strip() for p in raw.split(",")]
    if len(parts) != 2:
        raise ValueError("tokens must be in the form INPUT,OUTPUT (e.g. 123,456)")
    return int(parts[0]), int(parts[1])


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Track Anthropic API usage and costs.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # log command
    log_parser = subparsers.add_parser(
        "log", help="Log a single API call with token counts."
    )
    log_parser.add_argument(
        "--operation",
        "-o",
        required=True,
        help="Operation name (e.g., translate_text, generate_plan).",
    )
    log_parser.add_argument(
        "--tokens",
        "-t",
        required=True,
        help="Token counts as INPUT,OUTPUT (e.g., 1024,256).",
    )
    log_parser.add_argument(
        "--model",
        "-m",
        required=True,
        help="Model name (must match pricing keys in CostTracker, e.g. claude-3-5-sonnet-20241022).",
    )
    log_parser.add_argument(
        "--batch",
        action="signify_batch",
        help="Flag indicating this was a batch API call (uses batch pricing when available).",
    )

    # summary command
    subparsers.add_parser("summary", help="Print a summary of all logged costs.")

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    tracker = CostTracker()

    if args.command == "summary":
        tracker.print_summary()
        return 0

    if args.command == "log":
        try:
            input_tokens, output_tokens = _parse_tokens_pair(args.tokens)
        except Exception as exc:  # noqa: BLE001
            print(f"❌ Invalid --tokens value: {exc}", file=sys.stderr)
            return 1

        is_batch = getattr(args, "batch", False)
        try:
            entry = tracker.log_call(
                operation=args.operation,
                model=args.model,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                is_batch=is_batch,
            )
        except Exception as exc:  # noqa: BLE001
            print(f"❌ Failed to log call: {exc}", file=sys.stderr)
            return 1

        print(
            f"✅ Logged {entry['operation']} on {entry['model']}: "
            f"{entry['input_tokens']} in, {entry['output_tokens']} out, "
            f"cost ${entry['total_cost']:.6f}"
        )
        return 0

    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())


