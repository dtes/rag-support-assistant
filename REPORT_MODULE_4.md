# RAG System Performance Evaluation Report

**[Demo video](https://drive.google.com/file/d/1GMQpI4IfFaW4LdxmHwXNGxBdpU7HqkRk/view?usp=sharing)**

## Overview

This report presents a comprehensive evaluation of the RAG (Retrieval-Augmented Generation) system performance across different retrieval strategies. The evaluation focuses on varying key system parameters to determine their impact on system performance and answer quality.

## Testing Methodology

### API Testing Infrastructure

The RAG system is evaluated through its REST API endpoints. A dedicated debug endpoint `/chat/debug` was implemented specifically for testing and evaluation purposes. This endpoint extends the standard `/chat` response with additional debug information essential for metric calculation:

- **retrieved_docs**: Full document content retrieved during the RAG process
- **reranked_docs**: Documents after reranking (when enabled)
- **rewritten_query**: Query after rewriting transformations
- **routing_reason**: Explanation of the routing decision (RAG vs Tools)

The debug endpoint is utilized by the test suite (`backend/tests/test_rag_metrics.py`) to collect comprehensive data for RAGAS metric evaluation while maintaining separation from production traffic.

### Dataset Generation

The evaluation dataset was generated using Google's Gemini model, which was provided with the complete knowledge base documentation. This approach ensures:

- **Coverage**: Questions span the full range of system documentation
- **Relevance**: Questions reflect realistic user queries
- **Ground Truth**: High-quality reference answers for comparison
- **Consistency**: Standardized question-answer format across all test cases

The dataset consists of question-answer pairs with corresponding ground truth answers, stored in `backend/tests/dataset.json`.

## Evaluation Parameters

### Variable Configuration Parameters

1. **Chunking Method** `CHUNKING_METHOD`
   - `recursive` - RecursiveCharacterTextSplitter with fixed chunk size (800 characters, 100 overlap)
   - `semantic` - SemanticChunker with intelligent boundary detection

2. **Search Algorithm**: `SEARCH_METHOD`
   - `bm25` - BM25 lexical search for keyword-based retrieval
   - `vector` - Semantic vector search using embeddings

3. **Reranking**: `RERANK_ENABLED`
   - `true` - Cross-encoder reranking enabled
   - `false` - Reranking disabled

### Chunking Strategies: Detailed Comparison

#### RecursiveCharacterTextSplitter (Fixed Chunking)
A traditional approach that splits text at fixed character boundaries with configurable overlap.

**Advantages:**
- Predictable and consistent chunk sizes
- Fast processing with minimal computational overhead
- Simple to configure and tune
- Works well with uniform document structures

**Limitations:**
- May break semantic units mid-sentence or mid-paragraph
- Context boundaries are arbitrary rather than meaning-based
- Can split related concepts across multiple chunks
- Less effective for documents with varying structure

#### SemanticChunker (Semantic Chunking)
An advanced approach that uses embeddings to identify natural semantic boundaries in text, creating chunks based on meaning rather than character count.

**Configuration:**
- Breakpoint type: `percentile`
- Threshold: Configurable based on semantic similarity
- Embedding model: `all-MiniLM-L6-v2`

**Advantages:**
- Preserves semantic coherence within chunks
- Naturally respects paragraph and topic boundaries
- Better context preservation for complex topics
- Improves retrieval relevance by maintaining logical units
- Reduces information fragmentation across chunks

**Limitations:**
- Higher computational cost during indexing
- Variable chunk sizes may complicate some downstream processes
- Requires careful threshold tuning for optimal results
- Depends on embedding model quality

**Implementation Details:**
The system uses LangChain's `SemanticChunker` with HuggingFace embeddings. During document loading (`backend/loader.py`), the chunker analyzes text semantically and creates splits at natural boundaries where semantic similarity drops below the configured threshold.

## Evaluation Strategies

Three distinct strategies were evaluated:

1. **Fixed chaking. BM25 without Reranking**
   - `CHUNKING_METHOD=recursive`
   - `SEARCH_METHOD=bm25`
   - `RERANK_ENABLED=false`

2. **Fixed chaking. Semantic Search without Reranking**
   - `CHUNKING_METHOD=recursive`
   - `SEARCH_METHOD=vector`
   - `RERANK_ENABLED=false`

3. **Fixed chanking. Semantic Search with Reranking**
   - `CHUNKING_METHOD=recursive`
   - `SEARCH_METHOD=vector`
   - `RERANK_ENABLED=true`

4. **Semantic chanking. Semantic search without reranking**
   - `CHUNKING_METHOD=semantic`
   - `SEARCH_METHOD=vector`
   - `RERANK_ENABLED=false`

5. **Semantic chanking. Semantic search with reranking**
   - `CHUNKING_METHOD=semantic`
   - `SEARCH_METHOD=vector`
   - `RERANK_ENABLED=true`

## Evaluation Metrics

The following metrics were collected using the RAGAS framework, which evaluates RAG systems across multiple dimensions:

- **Answer Relevancy**: Measures how relevant the generated answer is to the user's question
- **Faithfulness**: Assesses whether the answer is grounded in the retrieved context (hallucination detection)
- **Context Precision**: Evaluates the accuracy and relevance of retrieved documents
- **Context Recall**: Measures the coverage of relevant information in retrieved documents
- **Overall**: Aggregate score across all metrics

### Results by Strategy

#### 1. Fixed Chunking + BM25 without Reranking (Baseline)

   | Metric            | Avg        | Min        | Max        | Δ from Baseline |
   | ----------------- | ---------- | ---------- | ---------- | --------------- |
   | Answer relevancy  | 0.4782     | 0.0000     | 0.9606     | -               |
   | Faithfulness      | 0.8394     | 0.3333     | 1.0000     | -               |
   | Context precision | 0.4574     | 0.0000     | 1.0000     | -               |
   | Context recall    | 0.5278     | 0.0000     | 1.0000     | -               |
   | **Overall**       | **0.5757** | **0.2250** | **0.9068** | **-**           |

#### 2. Fixed Chunking + Semantic Search without Reranking

   | Metric            | Avg        | Min        | Max        | Δ from Baseline |
   | ----------------- | ---------- | ---------- | ---------- | --------------- |
   | Answer relevancy  | 0.6294     | 0.0000     | 0.9618     | +31.6%          |
   | Faithfulness      | 0.7682     | 0.3750     | 1.0000     | -8.5%           |
   | Context precision | 0.5315     | 0.0000     | 1.0000     | +16.2%          |
   | Context recall    | 0.5778     | 0.0000     | 1.0000     | +9.5%           |
   | **Overall**       | **0.6267** | **0.2375** | **0.9317** | **+8.9%**       |

#### 3. Fixed Chunking + Semantic Search with Reranking

   | Metric            | Avg        | Min        | Max        | Δ from Baseline |
   | ----------------- | ---------- | ---------- | ---------- | --------------- |
   | Answer relevancy  | 0.8542     | 0.7480     | 0.9516     | +78.6%          |
   | Faithfulness      | 0.8469     | 0.5000     | 1.0000     | +0.9%           |
   | Context precision | 0.6296     | 0.0000     | 1.0000     | +37.6%          |
   | Context recall    | 0.4611     | 0.0000     | 1.0000     | -12.6%          |
   | **Overall**       | **0.6980** | **0.5121** | **0.9370** | **+21.2%**      |

#### 4. Semantic Chunking + Semantic Search without Reranking

   | Metric            | Avg        | Min        | Max        | Δ from Baseline |
   | ----------------- | ---------- | ---------- | ---------- | --------------- |
   | Answer relevancy  | 0.7074     | 0.0000     | 0.9630     | +47.9%          |
   | Faithfulness      | 0.8761     | 0.2857     | 1.0000     | +4.4%           |
   | Context precision | 0.8148     | 0.5000     | 1.0000     | +78.1%          |
   | Context recall    | 0.6519     | 0.2000     | 1.0000     | +23.5%          |
   | **Overall**       | **0.7626** | **0.3214** | **0.9496** | **+32.5%**      |

#### 5. Semantic Chunking + Semantic Search with Reranking (Best Performance)

   | Metric            | Avg        | Min        | Max        | Δ from Baseline |
   | ----------------- | ---------- | ---------- | ---------- | --------------- |
   | Answer relevancy  | 0.7804     | 0.4498     | 0.9213     | +63.2%          |
   | Faithfulness      | 0.9209     | 0.6667     | 1.0000     | +9.7%           |
   | Context precision | 0.8907     | 0.5000     | 1.0000     | +94.7%          |
   | Context recall    | 0.9259     | 0.6667     | 1.0000     | +75.5%          |
   | **Overall**       | **0.8795** | **0.7417** | **0.9786** | **+52.8%**      |

### System Metrics
- **Latency** - Response time in milliseconds
- **Cost/Token** - Cost per token processed

### Retrieval Metrics
- **Context Precision** - Accuracy of retrieved context
- **Recall** - Coverage of relevant documents

### Answer Quality Metrics (LLM-as-a-Judge)
- **Answer Relevance** - Relevance of generated answers to queries

## Results

### System Performance Notes

**Latency and Cost Analysis**: The latency and cost per token metrics showed minimal variation across the three strategies, indicating that the choice of search method and reranking does not significantly impact system performance overhead.

**Caching Implementation**: To further optimize system performance, exact-match caching (non-semantic) was implemented at each node level of graph RAG. This caching mechanism provides substantial improvements:

- **Latency Reduction**: Cached responses significantly decrease response time for repeated queries
- **Cost Optimization**: Token costs are dramatically reduced when serving cached results

## Production Observability with LangFuse

### Overview

The system implements comprehensive observability using **LangFuse**, an open-source LLM engineering platform that provides tracing, monitoring, and evaluation capabilities for production RAG systems.

### Implementation

**Automatic Tracing**: The LangGraph integration with LangFuse automatically captures:
- Complete request/response traces
- Token usage and costs
- Latency metrics at each pipeline stage
- Retrieved documents and their relevance scores
- LLM generations and intermediate steps

**Sampling Strategy**: To optimize costs and storage while maintaining representative monitoring, the system implements intelligent sampling:

```python
# Sampling configuration in settings
langfuse:
  enabled: true
  sample_rate: 0.1  # Sample 10% of production traffic
```

This approach:
- Reduces observability costs by 90%
- Maintains statistically significant sample sizes
- Captures diverse query patterns over time
- Allows trend analysis without complete data collection

### Production Metrics Collection

#### Available Metrics
LangFuse automatically collects most RAGAS-compatible metrics in production:
- **Latency**: End-to-end and per-stage response times
- **Token Usage**: Input/output tokens and associated costs
- **Answer Relevancy**: Can be evaluated via LLM-as-a-judge in production
- **Faithfulness**: Measurable using retrieved context and generated answers
- **Context Precision**: Calculable from retrieval scores

#### Ground Truth Challenge
**Ground Truth Limitation**: The `ground_truth` metric (used for context recall) is not available in production since we don't have reference answers for user queries.

**Mitigation Strategies**:

1. **LLM-Generated Ground Truth**
   - Use a strong LLM (e.g., GPT-4, Claude) to generate reference answers
   - Apply quality filters to ensure reliability
   - Use these for periodic quality assessments

2. **Subset Evaluation**
   - Evaluate metrics without ground truth (relevancy, faithfulness, precision)
   - Use these as primary production quality indicators
   - Periodically conduct full evaluation with manually annotated samples

3. **User Feedback Integration**
   - Collect implicit feedback (session duration, follow-up questions)
   - Implement explicit feedback mechanisms (thumbs up/down)
   - Correlate feedback with automated metrics

### Monitoring Workflow

1. **Real-time Monitoring**: LangFuse dashboard shows live metrics and traces
2. **Anomaly Detection**: Alert on metric degradation or unusual patterns
3. **A/B Testing**: Compare different configurations using sampled production data
4. **Continuous Improvement**: Use production insights to refine the system

### Benefits

- **Data-Driven Optimization**: Make decisions based on real user behavior
- **Cost Management**: Sampling reduces observability overhead
- **Quality Assurance**: Detect regressions before they impact users
- **Debugging**: Trace individual requests for troubleshooting
- **Performance Tracking**: Monitor system evolution over time

## Conclusions

### Key Findings

The comprehensive evaluation reveals several critical insights about RAG system optimization:

#### 1. Semantic Search Superiority
**Semantic search demonstrates significantly superior performance** (8.9% improvement) compared to BM25 lexical search for this financial domain use case. The vector-based semantic search approach effectively captures contextual and conceptual relationships within financial documents, leading to improved retrieval quality and answer relevance.

#### 2. Semantic Chunking Impact
**Semantic chunking provides substantial improvements** (+32.5% overall) over fixed-size chunking when combined with semantic search. By preserving semantic coherence and respecting natural topic boundaries, semantic chunking:
- Improves context precision by 78.1%
- Enhances context recall by 23.5%
- Maintains better semantic coherence for complex financial topics

#### 3. Reranking Effectiveness
**Reranking provides significant value** when properly configured. The combination of semantic chunking with reranking achieves the best overall performance (+52.8% improvement):
- Answer relevancy improved by 63.2%
- Context precision improved by 94.7%
- Context recall improved by 75.5%
- Faithfulness improved by 9.7%

The reranking step is particularly effective at refining retrieval results when combined with semantic chunking, as it can better distinguish between semantically coherent chunks.

#### 4. Optimal Configuration
**Best Performance**: Semantic Chunking + Semantic Search + Reranking
- Overall score: 0.8795 (52.8% improvement over baseline)
- Achieves excellent performance across all metrics
- Particularly strong in context precision (0.8907) and context recall (0.9259)

### Recommendations

Based on these findings:

1. **Adopt semantic chunking** as the primary chunking strategy for production
   - Significantly improves retrieval quality
   - Better preserves semantic context
   - Worth the additional computational cost during indexing

2. **Maintain reranking in the pipeline**
   - Provides substantial improvements when combined with semantic chunking
   - Critical for achieving high context precision and recall
   - Essential for production-quality RAG systems

3. **Use semantic search** as the primary retrieval method
   - Superior performance for domain-specific queries
   - Better captures conceptual relationships in financial documentation

4. **Monitor and optimize thresholds**
   - Semantic chunking thresholds should be tuned for your specific domain
   - Reranking parameters may benefit from domain-specific fine-tuning

5. **Leverage LangFuse for continuous improvement**
   - Monitor production performance with sampling
   - Use insights to guide further optimizations
   - Implement feedback loops for quality assurance

## Summary

This evaluation demonstrates the significant impact of advanced RAG techniques on system performance. The optimal configuration—combining semantic chunking, semantic search, and reranking—achieves a **52.8% improvement** over the baseline, with particularly strong gains in context precision (+94.7%) and context recall (+75.5%).

Key achievements:
- **Robust testing infrastructure**: Debug endpoint and RAGAS-based evaluation framework
- **Comprehensive dataset**: Gemini-generated questions covering full documentation scope
- **Proven optimizations**: Semantic chunking and reranking provide measurable benefits
- **Production readiness**: LangFuse integration enables continuous monitoring and improvement

The evaluation methodology, utilizing the `/chat/debug` endpoint and standardized metrics, provides a reproducible framework for ongoing system optimization and quality assurance in production environments.
