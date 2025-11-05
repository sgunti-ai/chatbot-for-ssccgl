""" 
SSC RAG Backend Application Package 
"""

__version__ = "1.0.0"
__author__ = "Sunil kumar"
__description__ = "RAG-powered question search system for SSC exams"

# Import main components for easier access
from .main import app
from .chroma_client import ChromaClient
from .s3_client import S3Client
from .question_processor import QuestionProcessor, create_question_processor
from .models import (
    QueryRequest, QueryResponse, MatchResponse,
    ProcessResponse, HealthResponse, SubjectsResponse
)

# Package-level exports
__all__ = [
    "app",
    "ChromaClient", 
    "S3Client",
    "QuestionProcessor",
    "create_question_processor",
    "QueryRequest",
    "QueryResponse", 
    "MatchResponse",
    "ProcessResponse",
    "HealthResponse",
    "SubjectsResponse"
]

# Package initialization
print(f"Initializing SSC RAG Backend {__version__}")
