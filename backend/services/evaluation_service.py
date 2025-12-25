"""
Evaluation Service - automatic quality assessment for RAG with Langfuse
"""
from typing import List, Dict, Any, Optional
from config.settings import settings
from observability.langfuse_client import LangFuseClient


class EvaluationService:
    """Service for evaluating RAG quality and logging to Langfuse"""

    def __init__(self):
        """Initialize the evaluation service"""
        self.langfuse_client = LangFuseClient.get_client() if LangFuseClient.is_enabled() else None
        self.llm_client = None

    def _get_llm_client(self):
        """Lazy load LLM client for evaluation"""
        if self.llm_client is None:
            from llm_client import create_llm_client
            self.llm_client = create_llm_client()
        return self.llm_client

    def evaluate_relevance(self, query: str, answer: str) -> float:
        """
        Evaluate how well the answer addresses the user's query

        Args:
            query: User's question
            answer: Generated answer

        Returns:
            Relevance score (0-1)
        """
        try:
            llm = self._get_llm_client()

            prompt = f"""You are an expert evaluator. Your task is to assess how well the given answer addresses the user's question.

User question: {query}

Answer: {answer}

Evaluate the relevance of the answer on a continuous scale from 0.0 to 1.0, where:
- 0.0 = The answer is completely irrelevant, incorrect, or does not address the question at all.
- 1.0 = The answer directly addresses the question and is fully relevant and complete.
- Values between 0.0 and 1.0 should reflect partial relevance and completeness:
  - ~0.2 = The answer is mostly irrelevant or only touches the topic superficially.
  - ~0.4 = The answer has some relevant points but misses most of what is required.
  - ~0.6 = The answer is generally relevant but incomplete or lacks important details.
  - ~0.8 = The answer is highly relevant and mostly complete, with only minor gaps or inaccuracies.

You may use any decimal value (for example, 0.15, 0.38, 0.64, 0.79, 0.93) to best represent the degree of relevance.

Consider:
- Does the answer directly respond to the question?
- Does it cover all key aspects implied by the question?
- Are there missing parts, irrelevancies, or inaccuracies?

Respond with ONLY a single number between 0.0 and 1.0."""

            response = llm.invoke([("system", "You are an expert evaluator."), ("human", prompt)])
            score_text = response.content.strip()

            # Parse score
            try:
                score = float(score_text)
                score = max(0.0, min(1.0, score))  # Clamp between 0 and 1
            except ValueError:
                print(f"⚠ Failed to parse relevance score: {score_text}")
                score = 0.5  # Default to neutral

            print(f"[Evaluation] Relevance score: {score:.2f}")
            return score

        except Exception as e:
            print(f"✗ Relevance evaluation failed: {e}")
            return 0.5  # Default to neutral

    def evaluate_faithfulness(self, answer: str, context: str) -> float:
        """
        Evaluate if the answer is grounded in the provided context

        Args:
            answer: Generated answer
            context: Context documents used

        Returns:
            Faithfulness score (0-1)
        """
        try:
            llm = self._get_llm_client()

            prompt = f"""You are an expert evaluator. Rate how faithful the answer is to the provided context.

Context:
{context}

Answer: {answer}

Rate the faithfulness on a scale of 0 to 1, where:
- 0 = Answer contradicts or has no basis in context
- 0.5 = Answer is partially grounded in context
- 1 = Answer is fully grounded in context with no hallucinations

Respond with ONLY a number between 0 and 1."""

            response = llm.invoke([("system", "You are an expert evaluator."), ("human", prompt)])
            score_text = response.content.strip()

            # Parse score
            try:
                score = float(score_text)
                score = max(0.0, min(1.0, score))
            except ValueError:
                print(f"⚠ Failed to parse faithfulness score: {score_text}")
                score = 0.5

            print(f"[Evaluation] Faithfulness score: {score:.2f}")
            return score

        except Exception as e:
            print(f"✗ Faithfulness evaluation failed: {e}")
            return 0.5

    def evaluate_context_precision(
        self,
        query: str,
        retrieved_docs: List[Dict[str, Any]]
    ) -> tuple[float, str]:
        """
        Evaluate the precision of retrieved documents (how many are relevant)

        Args:
            query: User's question
            retrieved_docs: Retrieved documents

        Returns:
            Tuple of (precision score 0-1, comment string)
        """
        if not retrieved_docs:
            return 0.0, "No documents retrieved"

        try:
            llm = self._get_llm_client()

            # Evaluate each document
            relevant_count = 0
            for doc in retrieved_docs:
                prompt = f"""You are an expert evaluator. Determine if this document is relevant to the user's question.

User question: {query}

Document:
{doc.get('content', '')[:500]}...

Is this document relevant? Respond with ONLY 'yes' or 'no'."""

                response = llm.invoke([("system", "You are an expert evaluator."), ("human", prompt)])
                answer = response.content.strip().lower()

                if 'yes' in answer:
                    relevant_count += 1

            precision = relevant_count / len(retrieved_docs)
            comment = f"Relevant docs: {relevant_count}/{len(retrieved_docs)}"

            print(f"[Evaluation] Context precision: {precision:.2f} ({comment})")
            return precision, comment

        except Exception as e:
            print(f"✗ Context precision evaluation failed: {e}")
            return 0.5, f"Evaluation error: {str(e)}"

    def evaluate_recall(
        self,
        query: str,
        answer: str,
        retrieved_docs: List[Dict[str, Any]]
    ) -> tuple[float, str]:
        """
        Evaluate recall: whether all necessary information was retrieved

        Args:
            query: User's question
            answer: Generated answer
            retrieved_docs: Retrieved documents

        Returns:
            Tuple of (recall score 0-1, comment string)
        """
        if not retrieved_docs:
            return 0.0, "No documents retrieved"

        try:
            llm = self._get_llm_client()

            # Combine all retrieved content
            context = "\n\n".join([doc.get('content', '')[:500] for doc in retrieved_docs])

            prompt = f"""You are an expert evaluator. Your task is to assess how well the retrieved documents cover the information needed to answer the user's question.

User question: {query}

Generated answer: {answer}

Retrieved context:
{context}

Evaluate the recall of the retrieved context on a continuous scale from 0.0 to 1.0, where:
- 0.0 = The retrieved documents contain none of the critical information needed to answer the question.
- 1.0 = The retrieved documents contain all the critical information needed to fully and correctly answer the question.
- Values between 0.0 and 1.0 should reflect partial coverage:
  - ~0.2 = very little relevant information is present.
  - ~0.4 = some relevant pieces are present, but most key points are missing.
  - ~0.6 = more than half of the required information is present, but important gaps remain.
  - ~0.8 = most key information is present, with only minor details missing.

You may use any decimal value (for example, 0.13, 0.47, 0.72, 0.95) to best reflect the degree of coverage.

Respond with ONLY a single number between 0.0 and 1.0."""

            response = llm.invoke([("system", "You are an expert evaluator."), ("human", prompt)])
            score_text = response.content.strip()

            # Parse score
            try:
                score = float(score_text)
                score = max(0.0, min(1.0, score))
            except ValueError:
                print(f"⚠ Failed to parse recall score: {score_text}")
                score = 0.5

            comment = f"Recall score based on {len(retrieved_docs)} documents"
            print(f"[Evaluation] Recall: {score:.2f} ({comment})")
            return score, comment

        except Exception as e:
            print(f"✗ Recall evaluation failed: {e}")
            return 0.5, f"Evaluation error: {str(e)}"

    def evaluate_rag_pipeline(
        self,
        query: str,
        answer: str,
        retrieved_docs: List[Dict[str, Any]]
    ) -> Dict[str, float]:
        """
        Comprehensive evaluation of the entire RAG pipeline

        Args:
            query: User's question
            answer: Generated answer
            retrieved_docs: Retrieved documents

        Returns:
            Dictionary with all evaluation scores
        """
        print(f"[Evaluation] Starting comprehensive RAG evaluation...")

        # Run all evaluations
        relevance_score = self.evaluate_relevance(query, answer)
        precision_score, _ = self.evaluate_context_precision(query, retrieved_docs)
        recall_score, _ = self.evaluate_recall(query, answer, retrieved_docs)

        scores = {
            'relevance': relevance_score,
            'context_precision': precision_score,
            'recall': recall_score,
        }

        # Calculate overall score
        scores['overall'] = sum(scores.values()) / len(scores)

        print(f"[Evaluation] Overall score: {scores['overall']:.2f}")
        print(f"[Evaluation] Scores: {scores}")

        return scores


# Global instance
_evaluation_service: Optional[EvaluationService] = None


def get_evaluation_service() -> EvaluationService:
    """Get or create the global evaluation service instance"""
    global _evaluation_service
    if _evaluation_service is None:
        _evaluation_service = EvaluationService()
    return _evaluation_service
