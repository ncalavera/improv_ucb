"""Cost tracking and logging for API usage."""

from pathlib import Path
from typing import Dict, Optional
from datetime import datetime
import json
import csv


class CostTracker:
    """Tracks and logs API costs."""
    
    # Pricing per million tokens (standard API pricing)
    PRICING = {
        "claude-haiku-4-5-20251001": {
            "input": 0.50,   # $0.50 per MTok
            "output": 2.50   # $2.50 per MTok
        },
        "claude-3-opus-20240229": {
            "input": 15.00,  # $15.00 per MTok
            "output": 75.00  # $75.00 per MTok
        },
        "claude-3-5-sonnet-20241022": {
            "input": 3.00,   # $3.00 per MTok
            "output": 15.00  # $15.00 per MTok
        }
    }
    
    # Batch API pricing (50% discount)
    BATCH_PRICING = {
        "claude-haiku-4-5-20251001": {
            "input": 0.25,   # $0.25 per MTok (50% of standard)
            "output": 1.25   # $1.25 per MTok (50% of standard)
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

