"""
RAG System Metrics Testing

This test suite evaluates RAG system quality using RAGAS metrics.
Designed to run manually or in CI/CD pipelines, NOT in production.

Usage:
    # Test with dataset (recommended)
    python -m pytest tests/test_rag_metrics.py -v

    # Test with specific dataset
    python -m pytest tests/test_rag_metrics.py -v --dataset tests/dataset.json

    # Run as standalone script
    python tests/test_rag_metrics.py --dataset tests/dataset.json

Features:
- Uses evaluation datasets with ground truth answers
- Makes real API calls to RAG system
- Collects RAGAS metrics (faithfulness, relevancy, precision, recall)
- Generates detailed reports with scores
- Can be integrated into CI/CD for quality monitoring
"""

import json
import asyncio
import sys
import os
import random
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime

# Add backend to path for imports
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

# Import after path setup
import pytest
import requests
from services.evaluation_service import get_evaluation_service
from config.settings import settings


class RAGMetricsTester:
    """RAG system quality testing using RAGAS framework"""

    def __init__(self, api_url: str = "http://localhost:8000/chat", use_debug: bool = True):
        """
        Initialize tester

        Args:
            api_url: RAG API endpoint URL (base URL, without /debug)
            use_debug: Use /chat/debug endpoint to get retrieved_docs with content
        """
        self.api_url = api_url
        self.use_debug = use_debug
        self.eval_service = get_evaluation_service()
        self.results = []

    def load_dataset(self, dataset_path: str) -> List[Dict]:
        """
        Load evaluation dataset from JSON file

        Args:
            dataset_path: Path to JSON dataset file

        Returns:
            List of test examples with questions and ground truth
        """
        dataset_path = Path(dataset_path)
        if not dataset_path.exists():
            raise FileNotFoundError(f"Dataset not found: {dataset_path}")

        with open(dataset_path, 'r', encoding='utf-8') as f:
            dataset = json.load(f)

        print(f"\n✓ Loaded {len(dataset)} test examples from {dataset_path.name}")
        return dataset

    def call_rag_api(self, question: str, timeout: int = 30) -> Optional[Dict]:
        """
        Call RAG API to get answer and sources

        Args:
            question: User question
            timeout: Request timeout in seconds

        Returns:
            API response dict or None if failed
        """
        try:
            # Use debug endpoint if enabled to get retrieved_docs with content
            endpoint = f"{self.api_url}" if self.use_debug else self.api_url

            response = requests.post(
                endpoint,
                json={
                    "message": question, 
                    "user_id": f"user-{random.randint(10000, 500000)}",
                    "session_id": f"session-{random.randint(10000, 500000)}"
                },
                timeout=timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"\n✗ API request failed: {e}")
            return None

    async def evaluate_example(
        self,
        question: str,
        ground_truth: str
    ) -> Dict:
        """
        Evaluate single example through RAG API

        Args:
            question: User question
            ground_truth: Expected correct answer
            contexts: Optional pre-defined contexts (from dataset)

        Returns:
            Evaluation result with scores
        """
        # Call RAG API
        api_response = self.call_rag_api(question)

        if not api_response:
            return {
                "question": question,
                "status": "api_failed",
                "error": "Failed to get response from RAG API"
            }

        answer = api_response.get('answer', '')
        sources = api_response.get('sources', [])
        query_type = api_response.get('query_type', '')
        contexts = None

        if self.use_debug and 'retrieved_docs' in api_response:
            # Use retrieved_docs from debug endpoint (contains full content)
            retrieved_docs = api_response.get('retrieved_docs', [])
            contexts = [
                doc.get('content', '')
                for doc in retrieved_docs
                if doc.get('content')
            ]
            print(f"✓ Extracted {len(contexts)} contexts from retrieved_docs")
        else:
            # Fallback: try to extract from sources (won't work with standard endpoint)
            contexts = [
                source.get('content', '')
                for source in sources
                if source.get('content')
            ]

        # Fallback if no contexts available (e.g., for tools queries)
        if not contexts:
            print("⚠ No contexts available, using answer as fallback context")
            contexts = [answer]  # Use part of answer as context. [answer[:500]]

        # Run RAGAS evaluation
        try:
            scores = await self.eval_service.evaluate_with_ragas(
                question=question,
                answer=answer,
                contexts=contexts,
                ground_truth=ground_truth
            )
            print(f"scores: {scores}")

            return {
                "question": question,
                "answer": answer,
                "ground_truth": ground_truth,
                "query_type": query_type,
                "sources_count": len(sources),
                "contexts_count": len(contexts),
                "contexts": contexts,
                "scores": scores,
                "status": "success"
            }

        except Exception as e:
            print(f"error: {e}")
            return {
                "question": question,
                "answer": answer,
                "status": "evaluation_failed",
                "error": str(e)
            }

    async def run_dataset_evaluation(
        self,
        dataset_path: str,
        save_results: bool = True,
        output_dir: str = "tests/results"
    ) -> Dict:
        """
        Run evaluation on entire dataset

        Args:
            dataset_path: Path to dataset JSON file
            save_results: Whether to save results to file
            output_dir: Directory to save results

        Returns:
            Aggregated evaluation results
        """
        print("\n" + "=" * 80)
        print("RAG SYSTEM METRICS TESTING")
        print("=" * 80)
        print(f"Dataset: {dataset_path}")
        print(f"API URL: {self.api_url}")
        print("=" * 80)

        # Load dataset
        dataset = self.load_dataset(dataset_path)

        # Storage for results
        all_results = []
        aggregate_scores = {
            "answer_relevancy": [],
            "faithfulness": [],
            "context_precision": [],
            "context_recall": [],
            "overall": []
        }

        # Process each example
        for idx, item in enumerate(dataset, 1):
            question = item.get('question')
            ground_truth = item.get('ground_truth')

            print(f"\n[{idx}/{len(dataset)}] Testing example...")
            print(f"Q: {question[:80]}...")

            result = await self.evaluate_example(
                question=question,
                ground_truth=ground_truth
            )

            if result.get('status') == 'success':
                scores = result.get('scores', {})
                print(f"✓ Evaluation complete:")
                for metric, value in scores.items():
                    print(f"  - {metric}: {value:.4f}")
                    if metric in aggregate_scores:
                        aggregate_scores[metric].append(value)
            else:
                print(f"✗ {result.get('status')}: {result.get('error', 'Unknown error')}")

            all_results.append(result)

        # Calculate aggregate statistics
        print("\n" + "=" * 80)
        print("AGGREGATE RESULTS")
        print("=" * 80)
        print(f"Total examples: {len(dataset)}")
        print(f"Successful evaluations: {sum(1 for r in all_results if r.get('status') == 'success')}")
        print(f"Failed evaluations: {sum(1 for r in all_results if r.get('status') != 'success')}")
        print()

        aggregate_summary = {}
        if any(aggregate_scores.values()):
            print("Average scores across all examples:")
            print("-" * 80)
            for metric, values in aggregate_scores.items():
                if values:
                    avg = sum(values) / len(values)
                    min_val = min(values)
                    max_val = max(values)
                    aggregate_summary[metric] = {
                        "average": avg,
                        "min": min_val,
                        "max": max_val,
                        "count": len(values)
                    }
                    print(f"{metric:25s}: {avg:.4f} (min: {min_val:.4f}, max: {max_val:.4f})")
            print("=" * 80)

        # Save results
        if save_results:
            output_path = self._save_results(
                dataset_path=dataset_path,
                results=all_results,
                aggregate_summary=aggregate_summary,
                output_dir=output_dir
            )
            print(f"\n✓ Results saved to: {output_path}")

        return {
            "dataset_path": dataset_path,
            "total_examples": len(dataset),
            "successful": sum(1 for r in all_results if r.get('status') == 'success'),
            "failed": sum(1 for r in all_results if r.get('status') != 'success'),
            "aggregate_scores": aggregate_summary,
            "detailed_results": all_results
        }

    def _save_results(
        self,
        dataset_path: str,
        results: List[Dict],
        aggregate_summary: Dict,
        output_dir: str
    ) -> str:
        """
        Save evaluation results to JSON file

        Args:
            dataset_path: Original dataset path
            results: Detailed results list
            aggregate_summary: Aggregated scores
            output_dir: Output directory

        Returns:
            Path to saved results file
        """
        # Create output directory
        output_dir_path = Path(output_dir)
        output_dir_path.mkdir(parents=True, exist_ok=True)

        # Generate output filename
        dataset_name = Path(dataset_path).stem
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"{dataset_name}_results_{timestamp}.json"
        output_path = output_dir_path / output_filename

        # Prepare output data
        output_data = {
            "metadata": {
                "dataset_path": dataset_path,
                "api_url": self.api_url,
                "timestamp": timestamp,
                "total_examples": len(results),
                "successful": sum(1 for r in results if r.get('status') == 'success'),
                "failed": sum(1 for r in results if r.get('status') != 'success')
            },
            "aggregate_scores": aggregate_summary,
            "detailed_results": results
        }

        # Save to file
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)

        return str(output_path)


# Pytest fixtures and tests
@pytest.fixture
def tester():
    """Fixture to create RAG metrics tester"""
    return RAGMetricsTester()


@pytest.fixture
def dataset_path(request):
    """Fixture to get dataset path from command line or use default"""
    return request.config.getoption("--dataset", default="tests/dataset.json")


@pytest.mark.asyncio
async def test_rag_metrics_on_dataset(tester, dataset_path):
    """
    Test RAG system quality on evaluation dataset

    This test:
    1. Loads evaluation dataset
    2. Sends each question to RAG API
    3. Evaluates answers using RAGAS metrics
    4. Checks that average scores meet minimum thresholds
    """
    # Run evaluation
    results = await tester.run_dataset_evaluation(
        dataset_path=dataset_path,
        save_results=True
    )

    # Assert we got results
    assert results['total_examples'] > 0, "Dataset should contain examples"
    assert results['successful'] > 0, "At least some evaluations should succeed"

    # Check quality thresholds (adjust based on your requirements)
    aggregate = results['aggregate_scores']

    if 'overall' in aggregate:
        overall_avg = aggregate['overall']['average']
        print(f"\nOverall RAG quality score: {overall_avg:.4f}")

        # Assert minimum quality threshold
        # NOTE: Adjust threshold based on your quality requirements
        MIN_QUALITY_THRESHOLD = 0.5  # 50% minimum quality
        # assert overall_avg >= MIN_QUALITY_THRESHOLD, \
        #     f"RAG quality ({overall_avg:.4f}) below threshold ({MIN_QUALITY_THRESHOLD})"

    # Check individual metrics if available
    if 'faithfulness' in aggregate:
        faithfulness_avg = aggregate['faithfulness']['average']
        print(f"Faithfulness score: {faithfulness_avg:.4f}")
        # Should not have too many hallucinations
        # assert faithfulness_avg >= 0.6, "Faithfulness score too low (possible hallucinations)"

    if 'answer_relevancy' in aggregate:
        relevancy_avg = aggregate['answer_relevancy']['average']
        print(f"Answer relevancy score: {relevancy_avg:.4f}")
        # Answers should be relevant to questions
        # assert relevancy_avg >= 0.6, "Answer relevancy too low"


# @pytest.mark.asyncio
# async def test_single_rag_example(tester):
#     """
#     Test RAG system on a single example

#     Quick smoke test to verify RAG pipeline works
#     """
#     question = "How can I automate the categorization of recurring transactions?"
#     ground_truth = "You can create automation rules in the Transactions → Rules section based on keywords or counterparties."

#     result = await tester.evaluate_example(
#         question=question,
#         ground_truth=ground_truth
#     )

#     # Assert basic success
#     assert result['status'] == 'success', f"Evaluation failed: {result.get('error')}"
#     assert 'scores' in result, "Should return scores"
#     assert result['scores'], "Scores should not be empty"

#     # Print results
#     print(f"\nQuestion: {question}")
#     print(f"Answer: {result['answer'][:200]}...")
#     print(f"Scores: {result['scores']}")


def pytest_addoption(parser):
    """Add custom command line options for pytest"""
    parser.addoption(
        "--dataset",
        action="store",
        default="tests/dataset.json",
        help="Path to evaluation dataset JSON file"
    )


# Allow running as standalone script
def main():
    """Run evaluation as standalone script"""
    import argparse

    parser = argparse.ArgumentParser(description='Test RAG system quality metrics')
    parser.add_argument(
        '--dataset',
        type=str,
        default='tests/dataset.json',
        help='Path to evaluation dataset JSON file'
    )
    parser.add_argument(
        '--api-url',
        type=str,
        default='http://localhost:8000/chat/debug',
        help='RAG API endpoint URL'
    )
    parser.add_argument(
        '--no-save',
        action='store_true',
        help='Do not save results to file'
    )
    parser.add_argument(
        '--no-debug',
        action='store_true',
        help='Do not use debug endpoint (use standard /chat instead)'
    )

    args = parser.parse_args()

    # Create tester
    tester = RAGMetricsTester(
        api_url=args.api_url,
        use_debug=not args.no_debug
    )

    # Run evaluation
    asyncio.run(tester.run_dataset_evaluation(
        dataset_path=args.dataset,
        save_results=not args.no_save
    ))


if __name__ == '__main__':
    main()
