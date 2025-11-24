"""Helper script to execute LLM prompts from template files via Anthropic.

CLI (minimal version):
    python scripts/run_prompt.py \\
        --template prompts/path/to/prompt.md \\
        --vars vars.json \\
        --output output.txt \\
        [--model claude-3-5-sonnet-20241022] \\
        [--operation name_for_cost_tracker]

This script:
  - Loads a markdown/plaintext prompt template.
  - Loads variables from a JSON file or inline JSON string.
  - Performs simple `.format(**vars)` substitution.
  - Calls Anthropic Messages API.
  - Saves the response to the output file.
  - Logs usage via `src.cost_tracker.CostTracker`.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any, Dict

from dotenv import load_dotenv

import anthropic  # type: ignore[import-untyped]

from src.cost_tracker import CostTracker


def _load_vars(raw: str) -> Dict[str, Any]:
    """Load variables from a JSON file path or inline JSON string."""
    potential_path = Path(raw)
    if potential_path.exists():
        with potential_path.open("r", encoding="utf-8") as f:
            return json.load(f)
    # Fallback: treat as raw JSON
    return json.loads(raw)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run an Anthropic prompt from a template file with JSON variables."
    )
    parser.add_argument(
        "--template",
        "-t",
        required=True,
        help="Path to prompt template markdown/text file.",
    )
    parser.add_argument(
        "--vars",
        "-v",
        required=True,
        help="Path to JSON vars file OR inline JSON string.",
    )
    parser.add_argument(
        "--output",
        "-o",
        required=True,
        help="Path to write LLM response.",
    )
    parser.add_argument(
        "--model",
        "-m",
        default="claude-3-5-sonnet-20241022",
        help="Anthropic model name (default: claude-3-5-sonnet-20241022).",
    )
    parser.add_argument(
        "--operation",
        help="Operation name for cost tracking (default: derived from template filename).",
    )
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=64000,
        help="Maximum tokens for LLM response (default: 64000, max for Claude Haiku/Sonnet 4.5).",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    load_dotenv()
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        parser.error("ANTHROPIC_API_KEY is not set in the environment or .env file.")

    template_path = Path(args.template)
    if not template_path.exists():
        parser.error(f"Template file not found: {template_path}")

    try:
        vars_dict = _load_vars(args.vars)
    except Exception as exc:  # noqa: BLE001
        parser.error(f"Failed to load vars from {args.vars}: {exc}")

    with template_path.open("r", encoding="utf-8") as f:
        template = f.read()

    try:
        prompt_text = template.format(**vars_dict)
    except Exception as exc:  # noqa: BLE001
        parser.error(f"Error applying vars to template: {exc}")

    client = anthropic.Anthropic(api_key=api_key)

    # Use streaming for long requests (required when max_tokens > 8K or request may take >10 min)
    use_streaming = args.max_tokens > 8000

    try:
        if use_streaming:
            # Stream the response for long requests
            full_response_text = ""
            with client.messages.stream(
                model=args.model,
                max_tokens=args.max_tokens,
                messages=[{"role": "user", "content": prompt_text}],
            ) as stream:
                for text in stream.text_stream:
                    full_response_text += text
                response = stream.get_final_message()
            text = full_response_text
        else:
            # Non-streaming for shorter requests
            response = client.messages.create(
                model=args.model,
                max_tokens=args.max_tokens,
                messages=[{"role": "user", "content": prompt_text}],
            )
            text = response.content[0].text if response.content else ""
    except Exception as exc:  # noqa: BLE001
        parser.error(f"Anthropic API call failed: {exc}")

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        f.write(text)

    # Log costs via CostTracker
    tracker = CostTracker()
    operation_name = (
        args.operation or f"run_prompt_{template_path.stem}"
    )
    input_tokens = getattr(response.usage, "input_tokens", 0)
    output_tokens = getattr(response.usage, "output_tokens", 0)
    tracker.log_call(
        operation=operation_name,
        model=args.model,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        is_batch=False,
        metadata={
            "template": str(template_path),
            "output": str(output_path),
        },
    )

    print(f"✅ Wrote LLM response to {output_path}")
    print(
        f"   Tokens: input={input_tokens}, output={output_tokens} "
        f"(operation={operation_name}, model={args.model})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


