"""
Evaluation Service - RAG quality assessment using RAGAS framework with new async API
"""
import os
# Fix GitPython "Bad git executable" error - disable git refresh on import
os.environ['GIT_PYTHON_REFRESH'] = 'quiet'

from typing import List, Dict, Any, Optional
from ragas import evaluate, EvaluationDataset, SingleTurnSample
from ragas.metrics import (
    Faithfulness,
    LLMContextRecall,
    ResponseRelevancy,
    ContextPrecision
)
from ragas.llms import LangchainLLMWrapper
from langchain_openai import ChatOpenAI, AzureChatOpenAI, AzureOpenAIEmbeddings, OpenAIEmbeddings
from config.settings import settings
from observability.langfuse_client import LangFuseClient
from sentence_transformers import SentenceTransformer


class SentenceTransformerWrapper:
    """Wrapper to make SentenceTransformer compatible with LangChain embeddings interface"""

    def __init__(self, model_name: str):
        self.model = SentenceTransformer(model_name)

    def embed_query(self, text: str) -> list:
        """Embed a single query text"""
        return self.model.encode(text).tolist()

    def embed_documents(self, texts: list) -> list:
        """Embed multiple documents"""
        return self.model.encode(texts).tolist()


class EvaluationService:
    """Service for evaluating RAG quality using RAGAS framework v0.4.2"""

    def __init__(self):
        """Initialize the evaluation service"""
        self.langfuse_client = LangFuseClient.get_client() if LangFuseClient.is_enabled() else None
        self.llm = None
        self.embeddings = None

    def _get_llm(self):
        """Get LangChain LLM wrapped for RAGAS evaluation"""
        if self.llm is None:
            if settings.llm.provider == "azure-openai":
                base_llm = AzureChatOpenAI(
                    azure_endpoint=settings.llm.azure_endpoint,
                    api_key=settings.llm.azure_api_key,
                    api_version=settings.llm.azure_api_version,
                    azure_deployment=settings.llm.azure_deployment,
                    temperature=0
                )
            else:
                base_llm = ChatOpenAI(
                    model=settings.llm.model or "gpt-4",
                    api_key=settings.llm.api_key,
                    temperature=0
                )
            # Wrap LangChain LLM for RAGAS v0.4
            self.llm = LangchainLLMWrapper(base_llm)
        return self.llm

    def _get_embeddings(self):
        """Get LangChain embeddings for RAGAS evaluation"""
        if self.embeddings is None:
            # Use local SentenceTransformer for embeddings to avoid Azure OpenAI access issues
            # This is more reliable and doesn't require API access
            self.embeddings = SentenceTransformerWrapper(settings.embedding.model)
        return self.embeddings

    def _get_enabled_metrics(self, has_ground_truth: bool = False) -> List:
        """
        Get list of enabled RAGAS metrics for v0.4.2

        Args:
            has_ground_truth: Whether ground truth is available in the dataset

        Returns:
            List of metric instances
        """
        # Available metrics mapping (v0.4 names)
        available_metrics = {
            "answer_relevancy": ResponseRelevancy,
            "faithfulness": Faithfulness,
            "context_precision": ContextPrecision,
            "context_recall": LLMContextRecall
        }

        # Metrics that require ground truth (reference)
        ground_truth_metrics = {"context_recall"}

        enabled_metrics = []

        for metric_name in settings.evaluation.metrics:
            # Skip metrics requiring ground truth if not available
            if metric_name in ground_truth_metrics and not has_ground_truth:
                print(f"⚠ Skipping '{metric_name}' - requires ground truth")
                continue

            if metric_name in available_metrics:
                # Instantiate metric class
                metric_class = available_metrics[metric_name]
                enabled_metrics.append(metric_class())
            else:
                print(f"⚠ Unknown metric '{metric_name}' in settings, skipping")

        # Default metrics if none configured
        if not enabled_metrics:
            print("⚠ No valid metrics configured, using default set")
            enabled_metrics = [ResponseRelevancy(), Faithfulness()]

            if has_ground_truth:
                enabled_metrics.extend([
                    ContextPrecision(),
                    LLMContextRecall()
                ])

        return enabled_metrics

    async def evaluate_with_ragas(
        self,
        question: str,
        answer: str,
        contexts: List[str],
        ground_truth: Optional[str] = None
    ) -> Dict[str, float]:
        """
        Evaluate RAG output using RAGAS framework with new async API

        Args:
            question: User's question
            answer: Generated answer
            contexts: List of context strings used for generation
            ground_truth: Optional ideal answer for evaluation

        Returns:
            Dictionary with evaluation scores
        """

        try:
            # Check if we have ground truth
            has_ground_truth = bool(ground_truth and settings.evaluation.use_ground_truth)

            # Get LLM and embeddings
            llm = self._get_llm()
            embeddings = self._get_embeddings()

            # Create SingleTurnSample for evaluation
            sample_kwargs = {
                "user_input": question,
                "response": answer,
                "retrieved_contexts": contexts
            }

            if has_ground_truth:
                sample_kwargs["reference"] = ground_truth

            sample = SingleTurnSample(**sample_kwargs)

            # Score each metric individually using the correct API
            scores = {}

            # Faithfulness - measures factual consistency
            if "faithfulness" in settings.evaluation.metrics:
                faithfulness_metric = Faithfulness(llm=llm)
                faith_result = await faithfulness_metric.single_turn_ascore(sample)
                scores["faithfulness"] = float(faith_result)

            # Answer Relevancy (ResponseRelevancy in new API)
            if "answer_relevancy" in settings.evaluation.metrics:
                answer_relevancy_metric = ResponseRelevancy(llm=llm, embeddings=embeddings)
                relevancy_result = await answer_relevancy_metric.single_turn_ascore(sample)
                scores["answer_relevancy"] = float(relevancy_result)

            # Context Precision
            if "context_precision" in settings.evaluation.metrics:
                context_precision_metric = ContextPrecision(llm=llm)
                precision_result = await context_precision_metric.single_turn_ascore(sample)
                scores["context_precision"] = float(precision_result)

            # Context Recall (requires ground truth)
            if "context_recall" in settings.evaluation.metrics:
                if has_ground_truth:
                    context_recall_metric = LLMContextRecall(llm=llm)
                    recall_result = await context_recall_metric.single_turn_ascore(sample)
                    scores["context_recall"] = float(recall_result)
                else:
                    print("⚠ Skipping 'context_recall' - requires ground truth")

            # Calculate overall score (average of all metrics)
            if scores:
                scores['overall'] = sum(scores.values()) / len(scores)

            print(f"[Evaluation] RAGAS evaluation completed: {scores}")

            # Log to Langfuse if enabled
            if self.langfuse_client:
                self._log_to_langfuse(question, answer, contexts, scores)

            return scores

        except Exception as e:
            print(f"✗ RAGAS evaluation failed: {e}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            return {}

    def evaluate_batch(
        self,
        questions: List[str],
        answers: List[str],
        contexts_list: List[List[str]],
        ground_truths: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Evaluate multiple RAG outputs in batch using RAGAS v0.4.2

        Args:
            questions: List of user questions
            answers: List of generated answers
            contexts_list: List of context lists (one per question)
            ground_truths: Optional list of ideal answers

        Returns:
            Dictionary with aggregated evaluation scores
        """

        try:
            # Check if we have ground truth
            has_ground_truth = bool(ground_truths and settings.evaluation.use_ground_truth)

            # Create RAGAS dataset - v0.4.2 expects EvaluationDataset
            data_dict = {
                "user_input": questions,           # v0.4: renamed from 'question'
                "response": answers,               # v0.4: renamed from 'answer'
                "retrieved_contexts": contexts_list  # v0.4: renamed from 'contexts'
            }

            # Add reference (ground truth) if provided and enabled
            if has_ground_truth:
                data_dict["reference"] = ground_truths  # v0.4: renamed from 'ground_truth'

            # Create EvaluationDataset (v0.4 requirement)
            dataset = EvaluationDataset.from_list(data_dict)

            # Get LLM and embeddings
            llm = self._get_llm()
            embeddings = self._get_embeddings()

            # Get enabled metrics
            metrics = self._get_enabled_metrics(has_ground_truth=has_ground_truth)

            if not metrics:
                print("⚠ No metrics available for evaluation")
                return {}

            print(f"[Evaluation] Running RAGAS batch evaluation on {len(questions)} samples...")

            # Run RAGAS evaluation (v0.4 API)
            result = evaluate(
                dataset=dataset,
                metrics=metrics,
                llm=llm,
                embeddings=embeddings
            )

            print(f"[Evaluation] RAGAS batch evaluation completed: {result}")

            return dict(result)

        except Exception as e:
            print(f"✗ RAGAS batch evaluation failed: {e}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            return {}

    def _log_to_langfuse(
        self,
        question: str,
        answer: str,
        contexts: List[str],
        scores: Dict[str, float]
    ):
        """Log evaluation metrics to Langfuse"""
        try:
            # Create a score for each metric
            for metric_name, score_value in scores.items():
                # Format metric name for Langfuse
                langfuse_metric_name = f"ragas_{metric_name}"

                # Log score to Langfuse
                self.langfuse_client.score(
                    name=langfuse_metric_name,
                    value=score_value,
                    comment=f"RAGAS evaluation: {metric_name}"
                )

            print(f"[Evaluation] Logged {len(scores)} metrics to Langfuse")

        except Exception as e:
            print(f"⚠ Failed to log evaluation metrics to Langfuse: {e}")


# Global instance
_evaluation_service: Optional[EvaluationService] = None


def get_evaluation_service() -> EvaluationService:
    """Get or create the global evaluation service instance"""
    global _evaluation_service
    if _evaluation_service is None:
        _evaluation_service = EvaluationService()
    return _evaluation_service
