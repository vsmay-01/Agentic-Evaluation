"""
Batch processing service for evaluating 1000s of agent responses.
Handles async processing, chunking, and progress tracking.
"""

from typing import List, Dict, Any, Callable
from ..models.request_model import EvaluationRequest, EvaluationInput
import asyncio
from concurrent.futures import ThreadPoolExecutor


class BatchProcessor:
    """Process large batches of evaluation requests."""
    
    def __init__(self, max_batch_size: int = 100, max_workers: int = 5):
        self.max_batch_size = max_batch_size
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
    
    def chunk_requests(self, inputs: List[EvaluationInput], chunk_size: int) -> List[List[EvaluationInput]]:
        """Split inputs into chunks for batch processing."""
        return [inputs[i:i + chunk_size] for i in range(0, len(inputs), chunk_size)]
    
    async def process_batch_async(
        self, 
        request_id: str,
        model_name: str,
        inputs: List[EvaluationInput],
        evaluate_func: Callable,
        progress_callback: Callable = None
    ) -> Dict[str, Any]:
        """
        Asynchronously process a batch of inputs.
        
        Args:
            request_id: Unique batch ID
            model_name: Agent model being evaluated
            inputs: List of evaluation inputs
            evaluate_func: Function to evaluate single input
            progress_callback: Optional callback for progress (processed_count, total_count)
        
        Returns:
            Aggregated results dict
        """
        chunks = self.chunk_requests(inputs, self.max_batch_size)
        all_results = []
        processed = 0
        total = len(inputs)
        
        for chunk in chunks:
            # Process chunk in parallel
            tasks = [
                asyncio.get_event_loop().run_in_executor(
                    self.executor,
                    evaluate_func,
                    request_id,
                    model_name,
                    inp
                )
                for inp in chunk
            ]
            
            chunk_results = await asyncio.gather(*tasks)
            all_results.extend(chunk_results)
            
            processed += len(chunk)
            if progress_callback:
                await progress_callback(processed, total)
        
        # Aggregate results
        return self._aggregate_batch_results(request_id, model_name, all_results)
    
    def _aggregate_batch_results(
        self,
        request_id: str,
        model_name: str,
        results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Aggregate individual evaluation results into batch summary."""
        
        if not results:
            return {
                "batch_id": request_id,
                "model_name": model_name,
                "total_evaluated": 0,
                "average_score": 0.0,
                "dimension_averages": {},
                "results": []
            }
        
        # Calculate averages
        scores = [r.get("score", 0) for r in results]
        average_score = sum(scores) / len(scores) if scores else 0
        
        # Dimension aggregation
        dimension_averages = {}
        for dim in ["instruction_following", "hallucination_prevention", "assumption_prevention", "coherence", "accuracy"]:
            values = []
            for r in results:
                dim_scores = r.get("details", {}).get("dimension_scores", {})
                if dim in dim_scores:
                    values.append(dim_scores[dim])
            if values:
                dimension_averages[dim] = sum(values) / len(values)
        
        # Score distribution
        score_distribution = {
            "excellent": len([s for s in scores if s >= 0.9]),      # 0.9-1.0
            "good": len([s for s in scores if 0.7 <= s < 0.9]),     # 0.7-0.9
            "fair": len([s for s in scores if 0.5 <= s < 0.7]),     # 0.5-0.7
            "poor": len([s for s in scores if s < 0.5]),            # <0.5
        }
        
        return {
            "batch_id": request_id,
            "model_name": model_name,
            "total_evaluated": len(results),
            "average_score": round(average_score, 4),
            "dimension_averages": {k: round(v, 4) for k, v in dimension_averages.items()},
            "score_distribution": score_distribution,
            "results": results,
            "summary": f"Evaluated {len(results)} responses. Avg score: {average_score:.2%}"
        }


# Global batch processor instance
batch_processor = BatchProcessor()
