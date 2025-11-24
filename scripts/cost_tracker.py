"""CLI wrapper for logging API usage and costs."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Tuple, Dict, Optional
from datetime import datetime
import json
import csv


class CostTracker:
    """Tracks and logs API costs.
    
    Pricing based on official Anthropic documentation:
    https://platform.claude.com/docs/en/about-claude/models/overview
    """
    
    # Pricing per million tokens (standard API pricing)
    # Source: https://platform.claude.com/docs/en/about-claude/models/overview
    PRICING = {
        # Claude 4.5 models (latest)
        "claude-sonnet-4-5-20250929": {
            "input": 3.00,   # $3.00 per MTok
            "output": 15.00  # $15.00 per MTok
        },
        "claude-haiku-4-5-20251001": {
            "input": 1.00,   # $1.00 per MTok
            "output": 5.00   # $5.00 per MTok
        },
        "claude-opus-4-1-20250805": {
            "input": 15.00,  # $15.00 per MTok
            "output": 75.00  # $75.00 per MTok
        },
        # Model aliases (point to latest versions)
        "claude-sonnet-4-5": {
            "input": 3.00,
            "output": 15.00
        },
        "claude-haiku-4-5": {
            "input": 1.00,
            "output": 5.00
        },
        "claude-opus-4-1": {
            "input": 15.00,
            "output": 75.00
        }
    }
    
    # Batch API pricing (50% discount on standard pricing)
    # Note: Batch pricing may vary by model - check official docs for latest rates
    BATCH_PRICING = {
        "claude-haiku-4-5-20251001": {
            "input": 0.50,   # $0.50 per MTok (50% of $1.00)
            "output": 2.50   # $2.50 per MTok (50% of $5.00)
        },
        "claude-haiku-4-5": {
            "input": 0.50,
            "output": 2.50
        }
    }
    
    def __init__(self, log_path: str = "data/api_costs.json", csv_path: str = "data/api_costs.csv"):
        """
        Initialize cost tracker.
        
        Args:
            log_path: Path to JSON log file (detailed)
            csv_path: Path to CSV log file (human-readable)
        """
        self.log_path = Path(log_path)
        self.csv_path = Path(csv_path)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        self.csv_path.parent.mkdir(parents=True, exist_ok=True)
        self._load_log()
        self._initialize_csv()
    
    def _load_log(self):
        """Load existing log file."""
        if self.log_path.exists():
            with open(self.log_path, 'r', encoding='utf-8') as f:
                self.log_data = json.load(f)
        else:
            self.log_data = {
                "total_cost": 0.0,
                "total_input_tokens": 0,
                "total_output_tokens": 0,
                "calls": []
            }
            self._save_log()
    
    def _save_log(self):
        """Save log to file."""
        with open(self.log_path, 'w', encoding='utf-8') as f:
            json.dump(self.log_data, f, indent=2, ensure_ascii=False)
        self._update_csv()
    
    def _initialize_csv(self):
        """Initialize CSV log file with headers."""
        if not self.csv_path.exists():
            with open(self.csv_path, 'w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'Date', 'Time', 'Task', 'Cost ($)', 'Input Tokens', 'Output Tokens', 
                    'Model', 'Batch', 'Details'
                ])
    
    def _update_csv(self):
        """Update CSV log file with all entries."""
        with open(self.csv_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            # Write header
            writer.writerow([
                'Date', 'Time', 'Task', 'Cost ($)', 'Input Tokens', 'Output Tokens', 
                'Model', 'Batch', 'Details'
            ])
            
            # Write entries
            for call in self.log_data.get('calls', []):
                timestamp = datetime.fromisoformat(call['timestamp'])
                date = timestamp.strftime('%Y-%m-%d')
                time = timestamp.strftime('%H:%M:%S')
                
                # Format task name
                task = call['operation'].replace('_', ' ').title()
                
                # Format details from metadata
                metadata = call.get('metadata', {})
                details_parts = []
                if 'chapter' in metadata:
                    details_parts.append(f"Chapter {metadata['chapter']}")
                if 'entries_count' in metadata:
                    details_parts.append(f"{metadata['entries_count']} entries")
                if 'estimated' in metadata and metadata['estimated']:
                    details_parts.append("(estimated)")
                details = ", ".join(details_parts) if details_parts else ""
                
                writer.writerow([
                    date,
                    time,
                    task,
                    f"${call['total_cost']:.6f}",
                    f"{call['input_tokens']:,}",
                    f"{call['output_tokens']:,}",
                    call['model'],
                    "Yes" if call.get('is_batch', False) else "No",
                    details
                ])
            
            # Add summary row
            writer.writerow([])
            writer.writerow(['TOTAL', '', '', f"${self.log_data['total_cost']:.6f}", 
                           f"{self.log_data['total_input_tokens']:,}", 
                           f"{self.log_data['total_output_tokens']:,}", '', '', ''])
    
    def _get_pricing(self, model: str, is_batch: bool = False) -> Dict[str, float]:
        """Get pricing for a model."""
        if is_batch and model in self.BATCH_PRICING:
            return self.BATCH_PRICING[model]
        return self.PRICING.get(model, {"input": 0.0, "output": 0.0})
    
    def log_call(
        self,
        operation: str,
        model: str,
        input_tokens: int,
        output_tokens: int,
        is_batch: bool = False,
        metadata: Optional[Dict] = None
    ):
        """
        Log an API call with cost calculation.
        
        Args:
            operation: Type of operation (e.g., "extract_frameworks", "translate")
            model: Model used
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            is_batch: Whether this was a batch API call
            metadata: Optional additional metadata
        """
        pricing = self._get_pricing(model, is_batch)
        
        # Calculate cost
        input_cost = (input_tokens / 1_000_000) * pricing["input"]
        output_cost = (output_tokens / 1_000_000) * pricing["output"]
        total_cost = input_cost + output_cost
        
        # Create log entry
        entry = {
            "timestamp": datetime.now().isoformat(),
            "operation": operation,
            "model": model,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "input_cost": round(input_cost, 6),
            "output_cost": round(output_cost, 6),
            "total_cost": round(total_cost, 6),
            "is_batch": is_batch,
            "metadata": metadata or {}
        }
        
        # Update totals
        self.log_data["total_cost"] += total_cost
        self.log_data["total_input_tokens"] += input_tokens
        self.log_data["total_output_tokens"] += output_tokens
        self.log_data["calls"].append(entry)
        
        self._save_log()
        
        return entry
    
    def get_summary(self) -> Dict:
        """Get cost summary."""
        return {
            "total_cost": round(self.log_data["total_cost"], 6),
            "total_input_tokens": self.log_data["total_input_tokens"],
            "total_output_tokens": self.log_data["total_output_tokens"],
            "total_calls": len(self.log_data["calls"]),
            "batch_calls": sum(1 for c in self.log_data["calls"] if c.get("is_batch", False)),
            "standard_calls": sum(1 for c in self.log_data["calls"] if not c.get("is_batch", False))
        }
    
    def print_summary(self):
        """Print cost summary to console."""
        summary = self.get_summary()
        print("\n" + "="*60)
        print("API Cost Summary")
        print("="*60)
        print(f"Total Cost: ${summary['total_cost']:.6f}")
        print(f"Total Input Tokens: {summary['total_input_tokens']:,}")
        print(f"Total Output Tokens: {summary['total_output_tokens']:,}")
        print(f"Total API Calls: {summary['total_calls']}")
        print(f"  - Batch calls: {summary['batch_calls']}")
        print(f"  - Standard calls: {summary['standard_calls']}")
        print("="*60)


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


