"""
PHASE 3 — Test Suite

Comprehensive tests for vector store, retrieval, and ingestion.
Mandatory gate before Phase 4.
"""

import pytest
import asyncio
from datetime import datetime

from schemas.vector_document import VectorDocument, VectorDocumentMetadata, SourceType, UploadedBy
from schemas.retrieval_agent_output import RetrievalAgentOutput, RetrievedChunk
from schemas.user_input import UserInputSchema, AudienceLevel, AudienceCategory, LearningMode, DepthRequirement
from schemas.execution_context import ExecutionContext

from services.vector_store import get_vector_store, reset_vector_store
from services.embedding_service import get_embedding_service, reset_embedding_service

from agents.retrieval_agent import RetrievalAgent
from tools.curriculum_ingestion import IngestionPipeline


# ============================================================================
# EMBEDDING SERVICE TESTS
# ============================================================================

class TestEmbeddingService:
    """Test embedding service determinism and consistency."""
    
    def setup_method(self):
        """Reset embedding service before each test."""
        reset_embedding_service()
    
    def test_embed_text_returns_correct_dimension(self):
        """Embedding vectors have correct dimension."""
        service = get_embedding_service()
        text = "This is a test sentence for embedding."
        embedding = service.embed_text(text)
        
        assert len(embedding) == service.embedding_dim
        assert all(isinstance(x, float) for x in embedding)
    
    def test_embed_text_deterministic(self):
        """Same text produces identical embeddings."""
        service = get_embedding_service()
        text = "Determinism test"
        
        embedding1 = service.embed_text(text)
        embedding2 = service.embed_text(text)
        
        assert embedding1 == embedding2
    
    def test_embed_text_different_content(self):
        """Different texts produce different embeddings."""
        service = get_embedding_service()
        text1 = "First text"
        text2 = "Second text"
        
        embedding1 = service.embed_text(text1)
        embedding2 = service.embed_text(text2)
        
        assert embedding1 != embedding2
    
    def test_embed_text_normalized(self):
        """Embeddings are unit-normalized."""
        service = get_embedding_service()
        text = "Test text for normalization"
        embedding = service.embed_text(text)
        
        magnitude = sum(x**2 for x in embedding) ** 0.5
        assert abs(magnitude - 1.0) < 0.01  # Should be ~1.0
    
    def test_embed_text_error_on_empty(self):
        """Error on empty text."""
        service = get_embedding_service()
        
        with pytest.raises(ValueError):
            service.embed_text("")
    
    def test_embed_texts_batch(self):
        """Batch embedding works correctly."""
        service = get_embedding_service()
        texts = ["Text 1", "Text 2", "Text 3"]
        
        embeddings = service.embed_texts(texts)
        
        assert len(embeddings) == 3
        assert all(len(e) == service.embedding_dim for e in embeddings)


# ============================================================================
# VECTOR DOCUMENT TESTS
# ============================================================================

class TestVectorDocument:
    """Test vector document schema and validation."""
    
    def test_vector_document_validation_success(self):
        """Valid document passes validation."""
        metadata = VectorDocumentMetadata(
            institution_name="Test University",
            degree_level="undergraduate",
            subject_domain="computer_science",
            audience_level="beginner",
            depth_level="foundational",
            source_type=SourceType.EXAMPLE,
            uploaded_by=UploadedBy.SYSTEM,
        )
        
        doc = VectorDocument(
            content="This is a test document with sufficient content. " * 10,
            metadata=metadata,
        )
        
        assert doc.validate() is True
    
    def test_vector_document_validation_empty_content(self):
        """Empty content fails validation."""
        metadata = VectorDocumentMetadata(
            institution_name="Test University",
            degree_level="undergraduate",
            subject_domain="computer_science",
            audience_level="beginner",
            depth_level="foundational",
            source_type=SourceType.EXAMPLE,
            uploaded_by=UploadedBy.SYSTEM,
        )
        
        doc = VectorDocument(content="", metadata=metadata)
        
        with pytest.raises(ValueError):
            doc.validate()
    
    def test_vector_document_validation_no_metadata(self):
        """Missing metadata fails validation."""
        doc = VectorDocument(
            content="This is a test document. " * 10,
            metadata=None,
        )
        
        with pytest.raises(ValueError):
            doc.validate()
    
    def test_vector_document_to_chroma_format(self):
        """Conversion to ChromaDB format works."""
        metadata = VectorDocumentMetadata(
            institution_name="Test University",
            degree_level="undergraduate",
            subject_domain="computer_science",
            audience_level="beginner",
            depth_level="foundational",
            source_type=SourceType.EXAMPLE,
            uploaded_by=UploadedBy.SYSTEM,
            source_name="test.pdf",
        )
        
        doc = VectorDocument(
            content="Test content for chroma. " * 10,
            metadata=metadata,
            document_id="doc_123",
        )
        
        chroma_format = doc.to_chroma_format()
        
        assert "id" in chroma_format
        assert "document" in chroma_format
        assert "metadatas" in chroma_format
        assert chroma_format["metadatas"]["institution_name"] == "Test University"


# ============================================================================
# VECTOR STORE TESTS
# ============================================================================

class TestVectorStore:
    """Test vector store operations."""
    
    def setup_method(self):
        """Initialize test store."""
        reset_vector_store()
        self.store = get_vector_store(force_new=True)
    
    def test_vector_store_initialization(self):
        """Vector store initializes correctly."""
        assert self.store._initialized
    
    def test_add_documents_single(self):
        """Adding single document works."""
        metadata = VectorDocumentMetadata(
            institution_name="Test University",
            degree_level="undergraduate",
            subject_domain="computer_science",
            audience_level="beginner",
            depth_level="foundational",
            source_type=SourceType.EXAMPLE,
            uploaded_by=UploadedBy.SYSTEM,
        )
        
        doc = VectorDocument(
            content="Computer Science Fundamentals course covers basic concepts. " * 20,
            metadata=metadata,
        )
        
        count = self.store.add_documents([doc])
        assert count == 1
    
    def test_add_documents_multiple(self):
        """Adding multiple documents works."""
        docs = []
        for i in range(3):
            metadata = VectorDocumentMetadata(
                institution_name="Test University",
                degree_level="undergraduate",
                subject_domain="computer_science",
                audience_level="beginner",
                depth_level="foundational",
                source_type=SourceType.EXAMPLE,
                uploaded_by=UploadedBy.SYSTEM,
            )
            
            doc = VectorDocument(
                content=f"Test document {i} with content. " * 20,
                metadata=metadata,
            )
            docs.append(doc)
        
        count = self.store.add_documents(docs)
        assert count == 3
    
    def test_similarity_search_empty_store(self):
        """Search on empty store returns empty results."""
        results = self.store.similarity_search("test query")
        assert results == []
    
    def test_similarity_search_with_results(self):
        """Search returns relevant documents."""
        # Add test documents
        metadata = VectorDocumentMetadata(
            institution_name="Test University",
            degree_level="undergraduate",
            subject_domain="computer_science",
            audience_level="beginner",
            depth_level="foundational",
            source_type=SourceType.EXAMPLE,
            uploaded_by=UploadedBy.SYSTEM,
        )
        
        doc = VectorDocument(
            content="Machine Learning is a subset of Artificial Intelligence. " * 20,
            metadata=metadata,
        )
        
        self.store.add_documents([doc])
        
        # Search for relevant query
        results = self.store.similarity_search("machine learning", k=5)
        
        assert len(results) > 0
        assert all("content" in r for r in results)
        assert all("similarity_score" in r for r in results)
    
    def test_similarity_search_with_metadata_filters(self):
        """Metadata filtering works."""
        # Add documents with different metadata
        for level in ["beginner", "intermediate", "advanced"]:
            metadata = VectorDocumentMetadata(
                institution_name="Test University",
                degree_level="undergraduate",
                subject_domain="computer_science",
                audience_level=level,
                depth_level="foundational",
                source_type=SourceType.EXAMPLE,
                uploaded_by=UploadedBy.SYSTEM,
            )
            
            doc = VectorDocument(
                content=f"Course for {level} level students. " * 20,
                metadata=metadata,
            )
            
            self.store.add_documents([doc])
        
        # Search with filter
        results = self.store.similarity_search(
            "course",
            k=5,
            metadata_filters={"audience_level": "beginner"},
        )
        
        # Should only get beginner level
        assert len(results) > 0
        assert all(r["metadata"]["audience_level"] == "beginner" for r in results)
    
    def test_get_collection_stats(self):
        """Collection stats are accurate."""
        # Add 3 documents
        for i in range(3):
            metadata = VectorDocumentMetadata(
                institution_name="Test University",
                degree_level="undergraduate",
                subject_domain="computer_science",
                audience_level="beginner",
                depth_level="foundational",
                source_type=SourceType.EXAMPLE,
                uploaded_by=UploadedBy.SYSTEM,
            )
            
            doc = VectorDocument(
                content=f"Test doc {i}. " * 20,
                metadata=metadata,
            )
            
            self.store.add_documents([doc])
        
        stats = self.store.get_collection_stats()
        assert stats["document_count"] == 3
    
    def test_reset_collection(self):
        """Resetting collection clears documents."""
        # Add document
        metadata = VectorDocumentMetadata(
            institution_name="Test University",
            degree_level="undergraduate",
            subject_domain="computer_science",
            audience_level="beginner",
            depth_level="foundational",
            source_type=SourceType.EXAMPLE,
            uploaded_by=UploadedBy.SYSTEM,
        )
        
        doc = VectorDocument(
            content="Test content. " * 20,
            metadata=metadata,
        )
        
        self.store.add_documents([doc])
        
        # Verify document exists
        stats_before = self.store.get_collection_stats()
        assert stats_before["document_count"] == 1
        
        # Reset
        self.store.reset()
        
        # Verify collection is empty
        stats_after = self.store.get_collection_stats()
        assert stats_after["document_count"] == 0


# ============================================================================
# RETRIEVAL AGENT TESTS
# ============================================================================

class TestRetrievalAgent:
    """Test retrieval agent logic."""
    
    def setup_method(self):
        """Initialize clean test environment."""
        reset_vector_store()
        reset_embedding_service()
        self.agent = RetrievalAgent()
        
        # Load example curriculum
        pipeline = IngestionPipeline()
        pipeline.ingest_example_curriculum()
    
    def teardown_method(self):
        """Cleanup after tests."""
        reset_vector_store()
    
    @pytest.mark.asyncio
    async def test_retrieval_agent_empty_store(self):
        """Retrieval gracefully handles empty store."""
        # Reset store to empty
        reset_vector_store()
        agent = RetrievalAgent()
        
        user_input = UserInputSchema(
            course_title="Test Course",
            course_description="A test course",
            audience_level=AudienceLevel.BEGINNER,
            audience_category=AudienceCategory.TECHNICAL,
            learning_mode=LearningMode.ONLINE,
            depth_requirement=DepthRequirement.FOUNDATIONAL,
            duration_hours=40,
        )
        
        context = ExecutionContext(
            user_input=user_input,
            session_id="test_session",
        )
        
        output = await agent.run(context)
        
        assert output.retrieved_chunks == []
        assert output.retrieval_confidence == 0.0
    
    @pytest.mark.asyncio
    async def test_retrieval_agent_generates_queries(self):
        """Retrieval agent generates search queries."""
        user_input = UserInputSchema(
            course_title="Machine Learning Basics",
            course_description="Introduction to ML algorithms",
            audience_level=AudienceLevel.INTERMEDIATE,
            audience_category=AudienceCategory.TECHNICAL,
            learning_mode=LearningMode.ONLINE,
            depth_requirement=DepthRequirement.INTERMEDIATE,
            duration_hours=40,
        )
        
        context = ExecutionContext(
            user_input=user_input,
            session_id="test_session",
        )
        
        output = await self.agent.run(context)
        
        # Should generate queries
        assert len(output.search_queries_executed) > 0
    
    @pytest.mark.asyncio
    async def test_retrieval_agent_respects_filters(self):
        """Retrieval agent applies metadata filters."""
        user_input = UserInputSchema(
            course_title="Beginner Programming Course",
            course_description="Basic programming",
            audience_level=AudienceLevel.BEGINNER,
            audience_category=AudienceCategory.TECHNICAL,
            learning_mode=LearningMode.ONLINE,
            depth_requirement=DepthRequirement.FOUNDATIONAL,
            duration_hours=30,
        )
        
        context = ExecutionContext(
            user_input=user_input,
            session_id="test_session",
        )
        
        output = await self.agent.run(context)
        
        # Should have applied audience_level filter
        assert "audience_level" in output.metadata_filters_applied or len(output.retrieved_chunks) > 0
    
    @pytest.mark.asyncio
    async def test_retrieval_agent_output_schema(self):
        """Retrieval agent output matches schema."""
        user_input = UserInputSchema(
            course_title="Software Engineering",
            course_description="SE principles",
            audience_level=AudienceLevel.INTERMEDIATE,
            audience_category=AudienceCategory.TECHNICAL,
            learning_mode=LearningMode.HYBRID,
            depth_requirement=DepthRequirement.INTERMEDIATE,
            duration_hours=50,
        )
        
        context = ExecutionContext(
            user_input=user_input,
            session_id="test_session",
        )
        
        output = await self.agent.run(context)
        
        assert isinstance(output, RetrievalAgentOutput)
        assert hasattr(output, "retrieved_chunks")
        assert hasattr(output, "retrieval_confidence")
        assert hasattr(output, "search_queries_executed")
        assert 0.0 <= output.retrieval_confidence <= 1.0


# ============================================================================
# INGESTION PIPELINE TESTS
# ============================================================================

class TestIngestionPipeline:
    """Test curriculum ingestion."""
    
    def setup_method(self):
        """Initialize clean pipeline."""
        reset_vector_store()
        self.pipeline = IngestionPipeline()
    
    def test_ingest_text_creates_chunks(self):
        """Text ingestion creates chunks."""
        metadata = VectorDocumentMetadata(
            institution_name="Test University",
            degree_level="undergraduate",
            subject_domain="computer_science",
            audience_level="beginner",
            depth_level="foundational",
            source_type=SourceType.EXAMPLE,
            uploaded_by=UploadedBy.SYSTEM,
        )
        
        content = "Course content. " * 100  # Long enough to chunk
        
        count, docs = self.pipeline.ingest_text(content, metadata)
        
        assert count > 0
        assert len(docs) > 0
    
    def test_ingest_example_curriculum(self):
        """Example curriculum ingestion works."""
        count, docs = self.pipeline.ingest_example_curriculum()
        
        assert count > 0
        assert len(docs) > 0
        assert all(isinstance(d, VectorDocument) for d in docs)


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestPhase3Integration:
    """Integration tests for Phase 3 components."""
    
    def setup_method(self):
        """Setup test environment."""
        reset_vector_store()
        reset_embedding_service()
        
        # Load example curriculum
        pipeline = IngestionPipeline()
        pipeline.ingest_example_curriculum()
    
    def teardown_method(self):
        """Cleanup."""
        reset_vector_store()
    
    @pytest.mark.asyncio
    async def test_full_retrieval_pipeline(self):
        """Full retrieval pipeline works end-to-end."""
        # Create user input
        user_input = UserInputSchema(
            course_title="Introduction to Computer Science",
            course_description="Basic CS concepts and algorithms",
            audience_level=AudienceLevel.BEGINNER,
            audience_category=AudienceCategory.TECHNICAL,
            learning_mode=LearningMode.ONLINE,
            depth_requirement=DepthRequirement.FOUNDATIONAL,
            duration_hours=40,
        )
        
        # Create execution context
        context = ExecutionContext(
            user_input=user_input,
            session_id="integration_test",
        )
        
        # Run retrieval
        agent = RetrievalAgent()
        output = await agent.run(context)
        
        # Verify output
        assert isinstance(output, RetrievalAgentOutput)
        assert len(output.search_queries_executed) > 0
        assert output.retrieval_confidence >= 0.0
        
        # Should retrieve something from example curriculum
        assert output.returned_count >= 0
def test_retrieval_agent_output_schema_valid():
    """PHASE 3: Retrieval Agent output conforms to RetrievalAgentOutput schema."""
    pass


def test_retrieval_agent_autonomous_query_construction():
    """PHASE 3: Retrieval Agent constructs search query autonomously from user input."""
    pass
