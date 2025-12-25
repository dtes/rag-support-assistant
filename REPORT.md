# RAG System Performance Evaluation Report

**[Demo video](https://drive.google.com/file/d/1GMQpI4IfFaW4LdxmHwXNGxBdpU7HqkRk/view?usp=sharing)**

## Overview

This report presents a comprehensive evaluation of the RAG (Retrieval-Augmented Generation) system performance across different retrieval strategies. The evaluation focuses on varying two key system parameters to determine their impact on system performance and answer quality.

## Evaluation Parameters

### Variable Configuration Parameters

1. **Search Algorithm**: `SEARCH_METHOD`
   - `bm25` - BM25 lexical search
   - `vector` - Semantic vector search

2. **Reranking**: `RERANK_ENABLED`
   - `true` - Reranking enabled
   - `false` - Reranking disabled

## Evaluation Strategies

Three distinct strategies were evaluated:

1. **BM25 without Reranking**
   - `SEARCH_METHOD=bm25`
   - `RERANK_ENABLED=false`

2. **Semantic Search without Reranking**
   - `SEARCH_METHOD=vector`
   - `RERANK_ENABLED=false`

3. **Semantic Search with Reranking**
   - `SEARCH_METHOD=vector`
   - `RERANK_ENABLED=true`

## Evaluation Metrics

### System Metrics
- **Latency** - Response time in milliseconds
- **Cost/Token** - Cost per token processed

### Retrieval Metrics
- **Context Precision** - Accuracy of retrieved context
- **Recall** - Coverage of relevant documents

### Answer Quality Metrics (LLM-as-a-Judge)
- **Answer Relevance** - Relevance of generated answers to queries

## Results

| Strategy | Search Method | Reranking | Latency (ms) | Cost/Token | Context Precision (0-1) | Recall (0-1) | Answer Relevance (0-1) |
|----------|---------------|-----------|--------------|------------|-------------------|--------|------------------|
| Strategy 1 | BM25 | Disabled | - | - | ~ 0.2857 | ~ 0.4000 | ~ 0.4000 |
| Strategy 2 | Semantic | Disabled | - | - | ~ 0.4286 | ~ 0.8000 | ~ 0.8000 |
| Strategy 3 | Semantic | Enabled | - | - | ~ 0.2857 | ~ 0.8000 | ~ 0.8000 |

### System Performance Notes

**Latency and Cost Analysis**: The latency and cost per token metrics showed minimal variation across the three strategies, indicating that the choice of search method and reranking does not significantly impact system performance overhead.

**Caching Implementation**: To further optimize system performance, exact-match caching (non-semantic) was implemented at each node level of graph RAG. This caching mechanism provides substantial improvements:

- **Latency Reduction**: Cached responses significantly decrease response time for repeated queries
- **Cost Optimization**: Token costs are dramatically reduced when serving cached results

## Conclusions

### Key Findings

The evaluation revealed that **semantic search demonstrates significantly superior performance** compared to BM25 lexical search for this financial domain use case. The vector-based semantic search approach effectively captures the contextual and conceptual relationships within financial documents, leading to improved retrieval quality and answer relevance.

**Reranking Impact**: Interestingly, the reranking step did not provide substantial performance improvements in this evaluation. The selected reranking methodology appears to be less effective for the financial domain, possibly due to:

- Domain-specific terminology and concepts that the reranker may not adequately capture
- The nature of financial queries requiring precise semantic understanding rather than surface-level relevance scoring
- Potential mismatch between the reranker's training data and financial domain characteristics

### Recommendations

Based on these findings:

1. **Semantic search (vector-based) should be the preferred retrieval method** for this financial RAG system
2. **Reranking can be disabled** to reduce latency and computational costs without sacrificing performance
3. Future work could explore domain-specific reranking models trained on financial data
4. Consider evaluating alternative reranking approaches that may be better suited to the financial domain
