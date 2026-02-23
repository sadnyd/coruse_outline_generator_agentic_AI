from utils.flow_logger import function_logger
"""
PHASE 3 — Curriculum Ingestion Pipeline

Offline/Admin flow to populate vector store with academic knowledge.
Takes PDFs, syllabi, outlines and chunks/embeds them for retrieval.
"""

import logging
from typing import List, Optional, Tuple
from pathlib import Path
from datetime import datetime

from schemas.vector_document import VectorDocument, VectorDocumentMetadata, SourceType, UploadedBy
from services.vector_store import get_vector_store


logger = logging.getLogger(__name__)


class IngestionPipeline:
    """
    Ingestion pipeline for academic knowledge.
    
    Stages:
    1. Load document
    2. Clean & normalize text
    3. Chunk content
    4. Attach metadata
    5. Store in vector DB
    """
    
    @function_logger("Handle __init__")
    def __init__(self, chunk_size_words: int = 500, chunk_overlap_words: int = 50):
        """
        Initialize ingestion pipeline.
        
        Args:
            chunk_size_words: Target chunk size in words
            chunk_overlap_words: Overlap between chunks
        """
        self.chunk_size_words = chunk_size_words
        self.chunk_overlap_words = chunk_overlap_words
        self.vector_store = get_vector_store()
    
    @function_logger("Execute ingest text")
    def ingest_text(
        self,
        content: str,
        metadata: VectorDocumentMetadata,
    ) -> Tuple[int, List[VectorDocument]]:
        """
        Ingest raw text content.
        
        Args:
            content: Raw text to ingest
            metadata: VectorDocumentMetadata for all chunks
            
        Returns:
            Tuple of (chunks_stored, list of VectorDocument)
        """
        logger.info(f"Ingesting content from {metadata.source_type.value}: {metadata.source_name}")
        
        # Clean & normalize text
        cleaned_content = self._clean_text(content)
        
        # Chunk content
        chunks = self._chunk_text(cleaned_content)
        
        logger.info(f"Created {len(chunks)} chunks from source")
        
        # Convert to VectorDocuments with metadata
        vector_docs = []
        for i, chunk in enumerate(chunks):
            doc = VectorDocument(
                content=chunk,
                metadata=metadata,
                chunk_index=i,
            )
            vector_docs.append(doc)
        
        # Store in vector DB
        try:
            stored_count = self.vector_store.add_documents(vector_docs)
            logger.info(f"Successfully stored {stored_count} chunks")
            return stored_count, vector_docs
        except Exception as e:
            logger.error(f"Failed to store chunks: {e}")
            return 0, []
    
    @function_logger("Execute ingest pdf")
    def ingest_pdf(
        self,
        file_path: str,
        institution_name: str,
        degree_level: str,
        subject_domain: str,
        audience_level: str,
        depth_level: str,
        source_type: SourceType = SourceType.UPLOADED_PDF,
        uploaded_by: UploadedBy = UploadedBy.USER,
        session_id: Optional[str] = None,
    ) -> Tuple[int, List[VectorDocument]]:
        """
        Ingest a PDF file.
        
        Args:
            file_path: Path to PDF file
            institution_name: Institution name
            degree_level: e.g., 'undergraduate', 'graduate'
            subject_domain: e.g., 'computer_science', 'engineering'
            audience_level: e.g., 'beginner', 'intermediate', 'advanced'
            depth_level: e.g., 'foundational', 'intermediate', 'advanced'
            source_type: Type of source
            uploaded_by: Who uploaded
            session_id: Optional session ID for user uploads
            
        Returns:
            Tuple of (chunks_stored, list of VectorDocument)
        """
        try:
            # Extract text from PDF
            text_content = self._extract_text_from_pdf(file_path)
            
            if not text_content:
                logger.warning(f"No text extracted from {file_path}")
                return 0, []
            
            # Create metadata
            metadata = VectorDocumentMetadata(
                institution_name=institution_name,
                degree_level=degree_level,
                subject_domain=subject_domain,
                audience_level=audience_level,
                depth_level=depth_level,
                source_type=source_type,
                uploaded_by=uploaded_by,
                source_name=Path(file_path).name,
                session_id=session_id,
            )
            
            # Ingest as text
            return self.ingest_text(text_content, metadata)
        
        except Exception as e:
            logger.error(f"Failed to ingest PDF {file_path}: {e}")
            return 0, []
    
    @staticmethod
    @function_logger("Execute  clean text")
    def _clean_text(text: str) -> str:
        """
        Clean and normalize text.
        
        Args:
            text: Raw text
            
        Returns:
            Cleaned text
        """
        # Remove extra whitespace
        text = " ".join(text.split())
        
        # Remove common artifacts
        text = text.replace("\n", " ")
        text = text.replace("\r", " ")
        
        # Normalize quotes
        text = text.replace(""", '"').replace(""", '"')
        text = text.replace("'", "'")
        
        return text.strip()
    
    @function_logger("Execute  chunk text")
    def _chunk_text(self, text: str) -> List[str]:
        """
        Chunk text into overlapping chunks.
        
        Args:
            text: Text to chunk
            
        Returns:
            List of text chunks
        """
        words = text.split()
        chunks = []
        
        i = 0
        while i < len(words):
            # Extract chunk of words
            chunk_words = words[i:i + self.chunk_size_words]
            chunk = " ".join(chunk_words)
            chunks.append(chunk)
            
            # Move by chunk size minus overlap
            i += self.chunk_size_words - self.chunk_overlap_words
        
        return chunks
    
    @staticmethod
    @function_logger("Execute  extract text from pdf")
    def _extract_text_from_pdf(file_path: str) -> Optional[str]:
        """
        Extract text from PDF file.
        
        Uses PyPDF2 if available, otherwise returns None.
        
        Args:
            file_path: Path to PDF
            
        Returns:
            Extracted text or None
        """
        try:
            import PyPDF2
            
            text_content = ""
            with open(file_path, "rb") as pdf_file:
                pdf_reader = PyPDF2.PdfReader(pdf_file)
                for page in pdf_reader.pages:
                    text_content += page.extract_text() + "\n"
            
            return text_content if text_content.strip() else None
        
        except ImportError:
            logger.warning("PyPDF2 not installed. PDF ingestion unavailable.")
            return None
        except Exception as e:
            logger.error(f"Error extracting PDF text: {e}")
            return None
    
    @function_logger("Execute ingest from folder")
    def ingest_from_folder(self, folder_path: str = "data/sample_curricula") -> Tuple[int, List[VectorDocument]]:
        """
        Scan and ingest all .txt files from a curriculum folder.
        
        This is the PRIMARY way to load real curriculum data!
        
        Args:
            folder_path: Path to folder containing .txt curriculum files
            
        Returns:
            Tuple of (chunks_stored, list of VectorDocument)
        """
        logger.info(f"Scanning curriculum folder: {folder_path}")
        
        folder = Path(folder_path)
        if not folder.exists():
            logger.error(f"Folder not found: {folder_path}")
            return 0, []
        
        txt_files = list(folder.glob("*.txt"))
        logger.info(f"Found {len(txt_files)} .txt files in {folder_path}")
        
        if not txt_files:
            logger.warning(f"No .txt files found in {folder_path}")
            return 0, []
        
        total_stored = 0
        all_docs = []
        
        for file_path in txt_files:
            logger.info(f"Ingesting: {file_path.name}")
            
            try:
                # Read file content
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                
                # Create metadata from filename (e.g., java.txt → Java)
                title = file_path.stem.replace("_", " ").title()
                
                metadata = VectorDocumentMetadata(
                    institution_name="Sample Curriculum Library",
                    degree_level="undergraduate",
                    subject_domain="computer_science",
                    audience_level="beginner",
                    depth_level="foundational",
                    source_type=SourceType.SYLLABUS,
                    uploaded_by=UploadedBy.SYSTEM,
                    source_name=title,
                    original_url=str(file_path.absolute()),
                )
                
                # Ingest the file
                stored_count, docs = self.ingest_text(content, metadata)
                total_stored += stored_count
                all_docs.extend(docs)
                
            except Exception as e:
                logger.error(f"Failed to ingest {file_path.name}: {e}")
                continue
        
        logger.info(f"Folder ingestion complete: {total_stored} total chunks stored from {len(txt_files)} files")
        return total_stored, all_docs

    @function_logger("Execute ingest example curriculum")
    def ingest_example_curriculum(self) -> Tuple[int, List[VectorDocument]]:
        """
        Ingest example curriculum data for testing.
        
        ⚠️  DEPRECATED: Use ingest_from_folder() instead to load real files!
        This method maintains backward compatibility with hardcoded examples.
        
        Returns:
            Tuple of (chunks_stored, list of VectorDocument)
        """
        logger.info("Ingesting example curriculum data (hardcoded fallback)")
        
        example_syllabi = [
            {
                "title": "Introduction to Computer Science",
                "content": (
                    "This foundational course covers basic CS concepts including algorithms, "
                    "data structures, and programming paradigms. Students will learn Python and "
                    "fundamental algorithmic thinking. Topics include: sorting algorithms, search, "
                    "graph theory basics, recursion, and dynamic programming. Prerequisites: none. "
                    "Audience: beginner-level undergraduates in technical fields."
                ),
                "degree_level": "undergraduate",
                "subject_domain": "computer_science",
                "audience_level": "beginner",
                "depth_level": "foundational",
            },
            {
                "title": "Software Engineering Principles",
                "content": (
                    "Intermediate course on software engineering practices and methodologies. "
                    "Covers SOLID principles, design patterns, refactoring, testing strategies, "
                    "and CI/CD pipelines. Students will work in teams on real projects. "
                    "Topics: Agile methodology, unit testing, integration testing, code reviews, "
                    "documentation, version control. Prerequisites: programming basics. "
                    "Audience: intermediate technical learners."
                ),
                "degree_level": "undergraduate",
                "subject_domain": "computer_science",
                "audience_level": "intermediate",
                "depth_level": "intermediate",
            },
            {
                "title": "Machine Learning Fundamentals",
                "content": (
                    "Foundation course on ML algorithms and theory. Students learn supervised learning, "
                    "unsupervised learning, evaluation metrics, cross-validation, and feature engineering. "
                    "Topics: linear regression, logistic regression, decision trees, clustering, neural networks basics, "
                    "and practical ML workflow. Tools: Python, scikit-learn, pandas. "
                    "Audience: intermediate to advanced technical learners with math background."
                ),
                "degree_level": "graduate",
                "subject_domain": "computer_science",
                "audience_level": "intermediate",
                "depth_level": "intermediate",
            },
            {
                "title": "Business Data Analytics",
                "content": (
                    "Applied analytics course for business professionals. Learn to extract insights from data "
                    "using Excel, SQL, and Tableau. Topics: data cleaning, exploratory data analysis, visualization, "
                    "statistical inference, A/B testing, dashboarding. Real case studies from retail and tech. "
                    "Audience: beginner to intermediate business professionals, non-technical background acceptable."
                ),
                "degree_level": "professional",
                "subject_domain": "business",
                "audience_level": "beginner",
                "depth_level": "foundational",
            },
            {
                "title": "Advanced Cloud Architecture",
                "content": (
                    "Deep dive into cloud architecture patterns and best practices. Covers microservices, "
                    "serverless design, containerization, database scaling, security in the cloud, disaster recovery. "
                    "On AWS, Azure, GCP platforms. Topics: IAM, networking, managed services, cost optimization. "
                    "Prerequisites: cloud fundamentals, Linux, networking. Audience: advanced technical practitioners."
                ),
                "degree_level": "graduate",
                "subject_domain": "computer_science",
                "audience_level": "advanced",
                "depth_level": "advanced",
            },
        ]
        
        total_stored = 0
        all_docs = []
        
        for syllabus in example_syllabi:
            metadata = VectorDocumentMetadata(
                institution_name="Example University",
                degree_level=syllabus["degree_level"],
                subject_domain=syllabus["subject_domain"],
                audience_level=syllabus["audience_level"],
                depth_level=syllabus["depth_level"],
                source_type=SourceType.EXAMPLE,
                uploaded_by=UploadedBy.SYSTEM,
                source_name=syllabus["title"],
            )
            
            stored_count, docs = self.ingest_text(syllabus["content"], metadata)
            total_stored += stored_count
            all_docs.extend(docs)
        
        logger.info(f"Example curriculum ingestion complete: {total_stored} total chunks stored")
        return total_stored, all_docs
