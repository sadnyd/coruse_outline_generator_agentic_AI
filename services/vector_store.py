"""
PHASE 3 — Vector Store Service

Vendor-agnostic vector database abstraction.
Currently ChromaDB, but replaceable with FAISS / Pinecone / Weaviate later.

Design rules:
- No agent logic
- No prompts
- No retries
- Pure data operations
"""

import os
from typing import List, Dict, Any, Optional
from pathlib import Path

from schemas.vector_document import VectorDocument, SourceType, UploadedBy
from services.embedding_service import get_embedding_service
from utils.flow_logger import function_logger


class VectorStore:
    """
    Vendor-agnostic vector database interface.
    Built to replace implementation without changing orchestrator code.
    """
    
    @function_logger("Initialize vector store")
    @function_logger("Handle __init__")
    def __init__(self, persist_directory: str = "./chroma_db", collection_name: str = "academic_knowledge"):
        """
        Initialize vector store.
        
        Args:
            persist_directory: Path to store vector DB (ChromaDB files)
            collection_name: Name of the collection
        """
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        self.collection = None
        self.client = None
        self._initialized = False
        
        # Embedding service for query encoding
        self.embedding_service = get_embedding_service()
        
        # Try to import ChromaDB; gracefully degrade if not available
        try:
            import chromadb
            self.chroma = chromadb
            self._has_chroma = True
        except ImportError:
            self._has_chroma = False
            print("⚠️  ChromaDB not installed. Using mock in-memory storage.")
            self._mock_storage = {}  # Simple dict-based fallback
    
    @function_logger("Initialize vector collection")
    @function_logger("Execute initialize")
    def initialize(self) -> bool:
        """
        Initialize the vector collection.
        
        Returns:
            bool: True if initialization succeeded
        """
        try:
            if self._has_chroma:
                os.makedirs(self.persist_directory, exist_ok=True)
                # Use new Chroma API (PersistentClient)
                try:
                    self.client = self.chroma.PersistentClient(
                        path=self.persist_directory
                    )
                except (TypeError, AttributeError):
                    # Fallback to old API if new one doesn't work
                    self.client = self.chroma.Client()
                
                self.collection = self.client.get_or_create_collection(
                    name=self.collection_name,
                    metadata={"hnsw:space": "cosine"}
                )
                self._initialized = True
                print(f"✅ VectorStore initialized with ChromaDB")
                return True
            else:
                # Mock initialization
                self._mock_storage[self.collection_name] = {"documents": []}
                self._initialized = True
                print(f"✅ VectorStore initialized (mock mode)")
                return True
        except Exception as e:
            print(f"❌ Failed to initialize VectorStore: {e}")
            return False
    
    @function_logger("Add documents to vector store")
    @function_logger("Add documents")
    def add_documents(self, documents: List[VectorDocument]) -> int:
        """
        Add documents to the vector store.
        
        Args:
            documents: List of VectorDocument instances
            
        Returns:
            Number of documents successfully added
        """
        if not self._initialized:
            raise RuntimeError("VectorStore not initialized. Call initialize() first.")
        
        if not documents:
            return 0
        
        # Validate all documents
        for doc in documents:
            doc.validate()
        
        # Generate embeddings
        texts = [doc.content for doc in documents]
        embeddings = self.embedding_service.embed_texts(texts)
        
        # Prepare for storage
        ids = []
        documents_list = []
        metadatas = []
        embeddings_list = []
        
        for doc, embedding in zip(documents, embeddings):
            chroma_doc = doc.to_chroma_format()
            ids.append(chroma_doc["id"])
            documents_list.append(chroma_doc["document"])
            metadatas.append(chroma_doc["metadatas"])
            embeddings_list.append(embedding)
        
        try:
            if self._has_chroma and self.collection:
                self.collection.add(
                    ids=ids,
                    documents=documents_list,
                    embeddings=embeddings_list,
                    metadatas=metadatas,
                )
            else:
                # Mock storage
                for doc_id, content, meta, emb in zip(ids, documents_list, metadatas, embeddings_list):
                    self._mock_storage[doc_id] = {
                        "content": content,
                        "metadata": meta,
                        "embedding": emb,
                    }
            
            return len(ids)
        except Exception as e:
            print(f"❌ Error adding documents: {e}")
            return 0
    
    @function_logger("Search for similar documents")
    @function_logger("Execute similarity search")
    def similarity_search(
        self,
        query: str,
        k: int = 5,
        metadata_filters: Optional[Dict[str, str]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Search for similar documents using vector similarity.
        
        Args:
            query: Search query text
            k: Number of results to return
            metadata_filters: Optional metadata filters (AND logic)
                e.g., {"audience_level": "beginner", "subject_domain": "cs"}
            
        Returns:
            List of results with content, score, metadata
        """
        if not self._initialized:
            raise RuntimeError("VectorStore not initialized. Call initialize() first.")
        
        if k < 1:
            raise ValueError("k must be >= 1")
        
        # Embed query
        query_embedding = self.embedding_service.embed_query(query)
        
        try:
            if self._has_chroma and self.collection:
                # Build where clause for metadata filters
                where = None
                if metadata_filters:
                    where = self._build_where_clause(metadata_filters)
                
                # Query
                results = self.collection.query(
                    query_embeddings=[query_embedding],
                    n_results=k,
                    where=where if where else None,
                )
                
                # Format results
                output = []
                if results and results["documents"] and len(results["documents"]) > 0:
                    docs = results["documents"][0]
                    distances = results["distances"][0] if results["distances"] else []
                    metas = results["metadatas"][0] if results["metadatas"] else []
                    ids = results["ids"][0] if results["ids"] else []
                    
                    for doc, dist, meta, doc_id in zip(docs, distances, metas, ids):
                        # Convert distance to similarity (cosine distance -> similarity)
                        similarity = 1 - dist if dist is not None else 0
                        output.append({
                            "content": doc,
                            "similarity_score": similarity,
                            "metadata": meta,
                            "document_id": doc_id,
                            "distance": dist,
                        })
                
                return output
            else:
                # Mock search (simple substring matching for testing)
                results = []
                for doc_id, doc_data in self._mock_storage.items():
                    if query.lower() in doc_data.get("content", "").lower():
                        results.append({
                            "content": doc_data["content"],
                            "similarity_score": 0.8,  # Mock score
                            "metadata": doc_data.get("metadata", {}),
                            "document_id": doc_id,
                        })
                
                return results[:k]
        
        except Exception as e:
            print(f"❌ Error in similarity search: {e}")
            return []
    
    @function_logger("Get vector collection statistics")
    @function_logger("Get collection stats")
    def get_collection_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the current collection.
        
        Returns:
            Stats dict with document count, etc.
        """
        if not self._initialized:
            return {"error": "VectorStore not initialized"}
        
        try:
            if self._has_chroma and self.collection:
                count = self.collection.count()
                return {
                    "collection_name": self.collection.name,
                    "document_count": count,
                    "embedding_model": self.embedding_service.get_config(),
                }
            else:
                return {
                    "document_count": len(self._mock_storage),
                    "storage_type": "mock",
                }
        except Exception as e:
            return {"error": str(e)}
    
    @function_logger("Delete entire collection")
    @function_logger("Delete collection")
    def delete_collection(self) -> bool:
        """
        DANGER: Delete entire collection (dev only).
        
        Returns:
            bool: True if deletion succeeded
        """
        try:
            if self._has_chroma and self.client:
                self.client.delete_collection(name=self.collection_name)
                self.collection = None
                self._initialized = False
                return True
            else:
                self._mock_storage.clear()
                return True
        except Exception as e:
            print(f"❌ Error deleting collection: {e}")
            return False
    
    @function_logger("Reset vector store to clean state")
    @function_logger("Execute reset")
    def reset(self) -> bool:
        """Reset store to clean state (dev only)."""
        success = self.delete_collection()
        if success:
            return self.initialize()
        return False
    
    @staticmethod
    @function_logger("Build ChromaDB where clause from filters")
    @function_logger("Build  where clause")
    def _build_where_clause(filters: Dict[str, str]) -> Optional[Dict[str, Any]]:
        """
        Build ChromaDB where clause from metadata filters.
        
        Args:
            filters: Filter dict like {"audience_level": "beginner"}
            
        Returns:
            ChromaDB where clause
        """
        if not filters:
            return None
        
        if len(filters) == 1:
            key, value = list(filters.items())[0]
            return {key: {"$eq": value}}
        else:
            # Multiple filters: AND logic
            clauses = [
                {key: {"$eq": value}}
                for key, value in filters.items()
            ]
            return {"$and": clauses}


# Singleton instance
_vector_store: Optional[VectorStore] = None


@function_logger("Get or create global vector store")
@function_logger("Get vector store")
def get_vector_store(force_new: bool = False, collection_name: str = "academic_knowledge") -> VectorStore:
    """
    Get or create the global vector store.
    
    Args:
        force_new: Create new instance (for testing)
        collection_name: Name of the collection
        
    Returns:
        VectorStore instance
    """
    global _vector_store
    
    if force_new or _vector_store is None:
        _vector_store = VectorStore(collection_name=collection_name)
        _vector_store.initialize()
    
    return _vector_store


@function_logger("Reset global vector store")
@function_logger("Execute reset vector store")
def reset_vector_store():
    """Reset the global vector store (for testing)."""
    global _vector_store
    if _vector_store:
        _vector_store.reset()
    _vector_store = None
