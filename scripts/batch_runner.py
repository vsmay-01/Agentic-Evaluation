"""
Batch runner script for submitting large batches of evaluations via HTTP API.
"""

import json
import requests
import time
import argparse
from pathlib import Path
from typing import List, Dict, Any
import sys


class BatchRunner:
    """Client for submitting and tracking batch evaluations."""
    
    def __init__(self, api_base: str = "http://localhost:8000"):
        self.api_base = api_base.rstrip('/')
        self.session = requests.Session()
    
    def submit_batch(self, batch_data: Dict[str, Any]) -> Dict[str, Any]:
        """Submit a batch for evaluation."""
        url = f"{self.api_base}/api/batch"
        response = self.session.post(url, json=batch_data)
        response.raise_for_status()
        return response.json()
    
    def get_batch_status(self, batch_id: str) -> Dict[str, Any]:
        """Get status of a batch evaluation."""
        url = f"{self.api_base}/api/batch/status/{batch_id}"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()
    
    def get_batch_result(self, batch_id: str) -> Dict[str, Any]:
        """Get final result of a completed batch."""
        url = f"{self.api_base}/api/batch/result/{batch_id}"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()
    
    def wait_for_completion(
        self,
        batch_id: str,
        poll_interval: int = 2,
        timeout: int = 3600
    ) -> Dict[str, Any]:
        """Wait for batch to complete and return result."""
        start_time = time.time()
        
        print(f"Waiting for batch {batch_id} to complete...")
        
        while True:
            if time.time() - start_time > timeout:
                raise TimeoutError(f"Batch {batch_id} did not complete within {timeout} seconds")
            
            status = self.get_batch_status(batch_id)
            
            if status.get("status") == "completed":
                print(f"Batch {batch_id} completed!")
                return self.get_batch_result(batch_id)
            elif status.get("status") == "failed":
                error = status.get("error", "Unknown error")
                raise RuntimeError(f"Batch {batch_id} failed: {error}")
            
            processed = status.get("processed", 0)
            total = status.get("total", 0)
            progress = (processed / total * 100) if total > 0 else 0
            print(f"Progress: {processed}/{total} ({progress:.1f}%)")
            
            time.sleep(poll_interval)
    
    def run_batch_from_file(
        self,
        file_path: Path,
        wait: bool = True
    ) -> Dict[str, Any]:
        """Load batch data from JSON file and submit."""
        with open(file_path, 'r', encoding='utf-8') as f:
            batch_data = json.load(f)
        
        print(f"Submitting batch from {file_path}...")
        result = self.submit_batch(batch_data)
        batch_id = result.get("batch_id")
        
        print(f"Batch submitted with ID: {batch_id}")
        
        if wait:
            return self.wait_for_completion(batch_id)
        else:
            return result


def main():
    parser = argparse.ArgumentParser(
        description="Submit and track batch evaluations"
    )
    parser.add_argument(
        "file",
        type=Path,
        help="Path to JSON file containing batch data"
    )
    parser.add_argument(
        "--api-base",
        default="http://localhost:8000",
        help="Base URL of the API (default: http://localhost:8000)"
    )
    parser.add_argument(
        "--no-wait",
        action="store_true",
        help="Don't wait for batch completion, just submit"
    )
    parser.add_argument(
        "--poll-interval",
        type=int,
        default=2,
        help="Polling interval in seconds (default: 2)"
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=3600,
        help="Timeout in seconds (default: 3600)"
    )
    
    args = parser.parse_args()
    
    if not args.file.exists():
        print(f"Error: File {args.file} does not exist", file=sys.stderr)
        sys.exit(1)
    
    runner = BatchRunner(api_base=args.api_base)
    
    try:
        result = runner.run_batch_from_file(
            args.file,
            wait=not args.no_wait
        )
        
        if args.no_wait:
            print(f"\nBatch submitted. Use batch ID to check status:")
            print(f"  GET {args.api_base}/api/batch/status/{result.get('batch_id')}")
        else:
            print("\n" + "="*60)
            print("BATCH RESULTS")
            print("="*60)
            print(json.dumps(result, indent=2))
            
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
