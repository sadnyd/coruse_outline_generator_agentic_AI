"""
PHASE 3 — Retrieval Agent

Intelligent knowledge retrieval without LLM hallucination.
Decides WHAT to retrieve based on user context.
vector_store handles HOW to retrieve.
"""

import logging
from typing import Optional, Dict, List, Any
from datetime import datetime

from schemas.user_input import UserInputSchema
from schemas.execution_context import ExecutionContext
from schemas.retrieval_agent_output import RetrievalAgentOutput, RetrievedChunk
from services.vector_store import get_vector_store
from utils.flow_logger import function_logger


# Configure logging
logger = logging.getLogger(__name__)


class RetrievalAgent:
    """
    Determines what knowledge to retrieve based on user input.
    
    Design:
    - NO LLM calls
    - NO hallucination
    - Pure deterministic logic
    - Explainable decisions
    """
    
    @function_logger("Handle __init__")
    @function_logger("Handle __init__")
    def __init__(self):
        """Initialize retrieval agent."""
        self.vector_store = get_vector_store()
        self.agent_name = "RetrievalAgent"
    
    @function_logger("Retrieve relevant curriculum knowledge from vector store")
    async def run(self, context: ExecutionContext) -> RetrievalAgentOutput:
        """
        Execute retrieval logic.
        
        Args:
            context: ExecutionContext with user_input, session_id, etc.
            
        Returns:
            RetrievalAgentOutput with retrieved chunks and metadata
            
        Raises:
            ValueError: If context is invalid
        """
        if not context:
            raise ValueError("ExecutionContext is required")
        
        if not context.user_input:
            raise ValueError("user_input in context is required")
        
        user_input = context.user_input
        execution_id = context.execution_id
        
        logger.info(f"[{execution_id}] RetrievalAgent.run() started")
        
        # Initialize output
        output = RetrievalAgentOutput(agent_name=self.agent_name)
        
        try:
            # Check if vector store has any documents
            stats = self.vector_store.get_collection_stats()
            doc_count = stats.get("document_count", 0)
            
            if doc_count == 0:
                logger.info(f"[{execution_id}] Vector store is empty. Retrieval skipped.")
                output.execution_notes = "Vector store is empty. No retrieval performed."
                output.retrieval_confidence = 0.0
                return output
            
            # Generate search queries based on user input
            search_queries = self._generate_search_queries(user_input)
            output.search_queries_executed = search_queries
            
            logger.info(f"[{execution_id}] Generated {len(search_queries)} search queries")
            
            # Build metadata filters
            metadata_filters = self._build_metadata_filters(user_input)
            output.metadata_filters_applied = list(metadata_filters.keys()) if metadata_filters else []
            
            logger.info(f"[{execution_id}] Applied filters: {metadata_filters}")
            
            # Execute searches and aggregate results
            all_results = []
            for query in search_queries:
                try:
                    results = self.vector_store.similarity_search(
                        query=query,
                        k=5,
                        metadata_filters=metadata_filters
                    )
                    all_results.extend(results)
                except Exception as e:
                    logger.warning(f"[{execution_id}] Search query failed: {e}")
                    continue
            
            output.total_hits = len(all_results)
            
            # Deduplicate and rank results
            unique_results = self._deduplicate_results(all_results)
            ranked_results = sorted(unique_results, key=lambda x: x["similarity_score"], reverse=True)
            
            # Keep top-k
            k = 5
            top_results = ranked_results[:k]
            output.returned_count = len(top_results)
            
            logger.info(f"[{execution_id}] Returned top-{k} results from {output.total_hits} total hits")
            
            # Convert to RetrievedChunk objects
            chunks = []
            for result in top_results:
                chunk = RetrievedChunk(
                    content=result["content"],
                    similarity_score=result["similarity_score"],
                    metadata=result["metadata"],
                    document_id=result["document_id"],
                    chunk_index=result.get("chunk_index", 0),
                )
                chunks.append(chunk)
            
            output.retrieved_chunks = chunks
            output.retrieval_confidence = self._calculate_confidence(top_results)
            output.knowledge_summary = self._summarize_knowledge(chunks, user_input)
            output.execution_notes = f"Successfully retrieved {len(chunks)} relevant chunks"
            
            logger.info(
                f"[{execution_id}] RetrievalAgent.run() completed. "
                f"Confidence: {output.retrieval_confidence:.2f}"
            )
            
            return output
        
        except Exception as e:
            logger.error(f"[{execution_id}] RetrievalAgent error: {e}")
            output.execution_notes = f"Error during retrieval: {str(e)}"
            output.retrieval_confidence = 0.0
            return output
    
    @function_logger("Execute  generate search queries")
    @function_logger("Execute  generate search queries")
    def _generate_search_queries(self, user_input: UserInputSchema) -> List[str]:
        """
        Generate search queries from course title and description only.
        
        Args:
            user_input: UserInputSchema
            
        Returns:
            List of search queries
        """
        queries = []
        
        # Query 1: Course title
        if user_input.course_title:
            queries.append(user_input.course_title)
        
        # Query 2: Description keywords
        if user_input.course_description:
            first_sentence = user_input.course_description.split(".")[0].strip()
            if first_sentence:
                queries.append(first_sentence)
        
        # Remove duplicates
        seen = set()
        unique_queries = []
        for q in queries:
            if q.lower() not in seen and q.strip():
                seen.add(q.lower())
                unique_queries.append(q.strip())
        
        return unique_queries[:3]  # Limit to 3 queries
    
    @function_logger("Build  metadata filters")
    @function_logger("Build  metadata filters")
    def _build_metadata_filters(self, user_input: UserInputSchema) -> Optional[Dict[str, str]]:
        """
        Build metadata filters for vector search.
        
        Args:
            user_input: UserInputSchema
            
        Returns:
            Metadata filter dict or None
        """
        filters = {}
        
        # Match audience level
        if user_input.audience_level:
            filters["audience_level"] = user_input.audience_level
        
        # Match subject domain (heuristic from audience category)
        if user_input.audience_category:
            category_to_domain = {
                "business": "business",
                "technical": "technical",
                "healthcare": "healthcare",
                "education": "education",
                "creative": "creative",
                "other": "other",
            }
            domain = category_to_domain.get(user_input.audience_category, "other")
            filters["subject_domain"] = domain
        
        return filters if filters else None
    
    @staticmethod
    @function_logger("Execute  deduplicate results")
    @function_logger("Execute  deduplicate results")
    def _deduplicate_results(results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Remove duplicate chunks from results.
        
        Args:
            results: Raw search results
            
        Returns:
            Deduplicated results
        """
        seen = set()
        unique = []
        
        for result in results:
            doc_id = result.get("document_id", "")
            if doc_id not in seen:
                seen.add(doc_id)
                unique.append(result)
        
        return unique
    
    @staticmethod
    @function_logger("Execute  calculate confidence")
    @function_logger("Execute  calculate confidence")
    def _calculate_confidence(top_results: List[Dict[str, Any]]) -> float:
        """
        Calculate confidence in retrieval quality.
        
        Logic:
        - Average similarity score of top results
        - Boosted if we have multiple highly-relevant results
        - Reduced if results are sparse
        
        Args:
            top_results: Top ranked results
            
        Returns:
            Confidence score (0.0 to 1.0)
        """
        if not top_results:
            return 0.0
        
        scores = [r.get("similarity_score", 0.0) for r in top_results]
        avg_score = sum(scores) / len(scores) if scores else 0.0
        
        # Boost confidence if we have multiple high-scoring results
        high_scores = sum(1 for s in scores if s > 0.7)
        boost = min(0.1, high_scores * 0.05)
        
        confidence = min(1.0, avg_score + boost)
        return confidence
    
    @staticmethod
    @function_logger("Execute  summarize knowledge")
    @function_logger("Execute  summarize knowledge")
    def _summarize_knowledge(chunks: List[RetrievedChunk], user_input: UserInputSchema) -> str:
        """
        Generate human-readable summary of retrieved knowledge.
        
        Args:
            chunks: Retrieved chunks
            user_input: User input for context
            
        Returns:
            Summary string
        """
        if not chunks:
            return "No relevant knowledge found in the institutional repository."
        
        # Count sources
        source_types = {}
        for chunk in chunks:
            src_type = chunk.metadata.get("source_type", "unknown")
            source_types[src_type] = source_types.get(src_type, 0) + 1
        
        source_summary = ", ".join(f"{count} {typ}" for typ, count in source_types.items())
        
        summary = (
            f"Retrieved {len(chunks)} relevant knowledge chunks "
            f"({source_summary}) aligned with '{user_input.course_title}' "
            f"for {user_input.audience_level} learners."
        )
        
        return summary
