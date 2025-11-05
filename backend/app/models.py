from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

# Request/Response Models for API

class QueryRequest(BaseModel):
    """Request model for querying questions"""
    question: str = Field(..., description="The question or topic to search for")
    top_k: int = Field(5, ge=1, le=50, description="Number of similar questions to return")
    subject: Optional[str] = Field(None, description="Filter by subject")

class MatchResponse(BaseModel):
    """Individual match response"""
    question: str = Field(..., description="The question text")
    options: List[str] = Field(default_factory=list, description="Available options")
    correct_answer: Optional[str] = Field(None, description="Correct answer")
    subject: str = Field(..., description="Question subject/category")
    similarity_score: float = Field(..., ge=0, le=1, description="Similarity score (0-1)")
    question_id: str = Field(..., description="Unique question identifier")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")

class QueryResponse(BaseModel):
    """Response model for query results"""
    question: str = Field(..., description="The original query question")
    matches: List[MatchResponse] = Field(..., description="List of similar questions")
    total_matches: int = Field(..., ge=0, description="Total number of matches found")
    search_time: Optional[float] = Field(None, description="Time taken for search in seconds")

class ProcessS3Request(BaseModel):
    """Request model for processing S3 files"""
    s3_bucket: str = Field(..., description="S3 bucket name")
    s3_key: str = Field(..., description="S3 object key")
    namespace: str = Field("ssc-questions", description="Namespace for vector storage")

class ProcessFileRequest(BaseModel):
    """Request model for processing local files"""
    file_path: str = Field(..., description="Path to the file to process")
    namespace: str = Field("ssc-questions", description="Namespace for vector storage")

class ProcessTextRequest(BaseModel):
    """Request model for processing text content"""
    text_content: str = Field(..., description="Text content to process")
    namespace: str = Field("ssc-questions", description="Namespace for vector storage")

class ProcessResponse(BaseModel):
    """Response model for processing operations"""
    job_id: str = Field(..., description="Unique job identifier")
    status: str = Field(..., description="Job status")
    message: str = Field(..., description="Status message")
    questions_processed: Optional[int] = Field(None, description="Number of questions processed")
    namespace: str = Field(..., description="Namespace where questions were stored")

class QuestionCreate(BaseModel):
    """Model for creating a new question"""
    text: str = Field(..., description="The question text")
    options: List[str] = Field(default_factory=list, description="Answer options")
    correct_answer: Optional[str] = Field(None, description="Correct answer")
    subject: str = Field(..., description="Question subject")
    year: Optional[int] = Field(None, description="Exam year")
    paper_type: Optional[str] = Field("CGL", description="Type of exam paper")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")

class QuestionUpdate(BaseModel):
    """Model for updating a question"""
    text: Optional[str] = Field(None, description="The question text")
    options: Optional[List[str]] = Field(None, description="Answer options")
    correct_answer: Optional[str] = Field(None, description="Correct answer")
    subject: Optional[str] = Field(None, description="Question subject")
    year: Optional[int] = Field(None, description="Exam year")
    paper_type: Optional[str] = Field(None, description="Type of exam paper")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")

class QuestionResponse(BaseModel):
    """Response model for question operations"""
    id: str = Field(..., description="Unique question identifier")
    text: str = Field(..., description="The question text")
    options: List[str] = Field(..., description="Answer options")
    correct_answer: Optional[str] = Field(None, description="Correct answer")
    subject: str = Field(..., description="Question subject")
    year: Optional[int] = Field(None, description="Exam year")
    paper_type: Optional[str] = Field(None, description="Type of exam paper")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")

class BatchQuestionsRequest(BaseModel):
    """Request model for batch question operations"""
    questions: List[QuestionCreate] = Field(..., description="List of questions to create")

class BatchQuestionsResponse(BaseModel):
    """Response model for batch operations"""
    processed: int = Field(..., description="Number of questions processed")
    failed: int = Field(..., description="Number of questions that failed")
    errors: List[str] = Field(default_factory=list, description="Error messages")

class HealthResponse(BaseModel):
    """Health check response"""
    status: str = Field(..., description="Service status")
    service: str = Field(..., description="Service name")
    timestamp: datetime = Field(..., description="Current timestamp")
    version: str = Field(..., description="API version")
    database_status: Optional[str] = Field(None, description="Database connection status")

class SubjectsResponse(BaseModel):
    """Available subjects response"""
    subjects: List[str] = Field(..., description="List of available subjects")

class StatsResponse(BaseModel):
    """Statistics response"""
    total_questions: int = Field(..., description="Total number of questions")
    subjects_count: Dict[str, int] = Field(..., description="Count by subject")
    recent_processing: Dict[str, Any] = Field(..., description="Recent processing stats")
    vector_db_status: str = Field(..., description="Vector database status")

class ErrorResponse(BaseModel):
    """Error response model"""
    error: str = Field(..., description="Error message")
    code: str = Field(..., description="Error code")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    timestamp: datetime = Field(..., description="When the error occurred")

class SearchFilters(BaseModel):
    """Search filters model"""
    subjects: Optional[List[str]] = Field(None, description="Filter by subjects")
    years: Optional[List[int]] = Field(None, description="Filter by years")
    paper_types: Optional[List[str]] = Field(None, description="Filter by paper types")
    min_similarity: Optional[float] = Field(0.5, ge=0, le=1, description="Minimum similarity score")

class AdvancedQueryRequest(BaseModel):
    """Advanced query request with filters"""
    question: str = Field(..., description="The question or topic to search for")
    top_k: int = Field(5, ge=1, le=50, description="Number of similar questions to return")
    filters: Optional[SearchFilters] = Field(None, description="Search filters")

# Internal Data Models (for database operations)

class QuestionData(BaseModel):
    """Internal question data model"""
    id: str
    text: str
    options: List[str]
    correct_answer: Optional[str]
    subject: str
    year: Optional[int]
    paper_type: Optional[str]
    full_text: str
    metadata: Dict[str, Any]
    embedding: Optional[List[float]] = None

    class Config:
        arbitrary_types_allowed = True

class ProcessingResult(BaseModel):
    """Internal processing result model"""
    success: bool
    questions_processed: int
    errors: List[str]
    namespace: str
    processing_time: float

class VectorSearchResult(BaseModel):
    """Internal vector search result model"""
    question: str
    options: List[str]
    correct_answer: Optional[str]
    subject: str
    similarity_score: float
    question_id: str
    metadata: Dict[str, Any]
    embedding: Optional[List[float]] = None

    class Config:
        arbitrary_types_allowed = True

# Utility Models

class PaginationParams(BaseModel):
    """Pagination parameters"""
    page: int = Field(1, ge=1, description="Page number")
    page_size: int = Field(10, ge=1, le=100, description="Page size")

class PaginatedResponse(BaseModel):
    """Paginated response model"""
    items: List[Any]
    total: int
    page: int
    page_size: int
    total_pages: int

class SuccessResponse(BaseModel):
    """Generic success response"""
    success: bool = True
    message: str
    data: Optional[Dict[str, Any]] = None

# Export all models
__all__ = [
    "QueryRequest",
    "MatchResponse", 
    "QueryResponse",
    "ProcessS3Request",
    "ProcessFileRequest",
    "ProcessTextRequest",
    "ProcessResponse",
    "QuestionCreate",
    "QuestionUpdate", 
    "QuestionResponse",
    "BatchQuestionsRequest",
    "BatchQuestionsResponse",
    "HealthResponse",
    "SubjectsResponse",
    "StatsResponse",
    "ErrorResponse",
    "SearchFilters",
    "AdvancedQueryRequest",
    "QuestionData",
    "ProcessingResult", 
    "VectorSearchResult",
    "PaginationParams",
    "PaginatedResponse",
    "SuccessResponse"
]
