import os
import uuid
from datetime import datetime

from fastapi import BackgroundTasks, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

# Import our models and clients
from .models import (AdvancedQueryRequest, BatchQuestionsRequest,
                     BatchQuestionsResponse, HealthResponse,
                     MatchResponse, ParseTextResponse,
                     ProcessResponse, ProcessS3Request,
                     ProcessTextRequest, QueryRequest, QueryResponse,
                     QuestionCreate, QuestionResponse, StatsResponse,
                     SubjectsResponse, SuccessResponse)
from .question_processor import create_question_processor
from .s3_client import S3Client


# Lazy chroma client: defer importing heavy ML and Chroma deps until first use.
class LazyChromaClient:
    def __init__(self):
        self._client = None

    def _ensure(self):
        if self._client is None:
            try:
                from .chroma_client import ChromaClient
            except Exception as e:
                raise RuntimeError("ChromaClient import failed: " + str(e))
            self._client = ChromaClient()
        return self._client

    def __getattr__(self, name):
        return getattr(self._ensure(), name)


app = FastAPI(
    title="SSC Question RAG API",
    description="RAG-powered question search system for SSC exam preparation",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize clients (chroma is lazy)
s3_client = S3Client()
chroma_client = LazyChromaClient()
question_processor = create_question_processor()

# Store processing jobs (in production, use Redis or database)
processing_jobs = {}


@app.get("/", response_model=SuccessResponse)
async def root():
    """Root endpoint with API information"""
    return SuccessResponse(
        message="SSC Question RAG API",
        data={
            "version": "1.0.0",
            "description": "RAG-powered question search for SSC exams",
            "endpoints": {
                "search": "/query",
                "subjects": "/subjects",
                "health": "/health",
                "stats": "/stats",
                "upload": "/process-file",
            },
        },
    )


@app.post("/query", response_model=QueryResponse)
async def query_questions(request: QueryRequest):
    """Query similar questions from vector store"""
    try:
        start_time = datetime.now()

        if request.subject:
            results = chroma_client.search_by_subject(request.question, request.subject, request.top_k)
        else:
            results = chroma_client.semantic_search(request.question, request.top_k)

        search_time = (datetime.now() - start_time).total_seconds()

        # Convert to MatchResponse objects
        match_responses = [
            MatchResponse(
                question=match["question"],
                options=match["options"],
                correct_answer=match["correct_answer"],
                subject=match["subject"],
                similarity_score=match["similarity_score"],
                question_id=match["question_id"],
            )
            for match in results
        ]

        return QueryResponse(
            question=request.question,
            matches=match_responses,
            total_matches=len(match_responses),
            search_time=search_time,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/query-advanced", response_model=QueryResponse)
async def advanced_query(request: AdvancedQueryRequest):
    """Advanced query with filters"""
    try:
        start_time = datetime.now()

        # For now, we'll use basic semantic search
        # In future, implement filter support in ChromaClient
        results = chroma_client.semantic_search(request.question, request.top_k)

        search_time = (datetime.now() - start_time).total_seconds()

        match_responses = [
            MatchResponse(
                question=match["question"],
                options=match["options"],
                correct_answer=match["correct_answer"],
                subject=match["subject"],
                similarity_score=match["similarity_score"],
                question_id=match["question_id"],
            )
            for match in results
        ]

        return QueryResponse(
            question=request.question,
            matches=match_responses,
            total_matches=len(match_responses),
            search_time=search_time,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/process-s3-file", response_model=ProcessResponse)
async def process_s3_file(request: ProcessS3Request, background_tasks: BackgroundTasks):
    """Process PDF from S3 and add to vector store"""
    try:
        job_id = str(uuid.uuid4())

        # Store job info
        processing_jobs[job_id] = {
            "status": "processing",
            "message": "File processing started",
            "started_at": datetime.now(),
        }

        # Download and process in background
        background_tasks.add_task(
            process_s3_file_background, job_id, request.s3_bucket, request.s3_key, request.namespace
        )

        return ProcessResponse(
            job_id=job_id,
            status="processing",
            message="File processing started in background",
            namespace=request.namespace,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/process-file", response_model=ProcessResponse)
async def process_file(file: UploadFile = File(...), namespace: str = "ssc-questions"):
    """Process uploaded file"""
    try:
        if not file.filename.lower().endswith(".pdf"):
            raise HTTPException(status_code=400, detail="Only PDF files are supported")

        job_id = str(uuid.uuid4())

        # Save uploaded file temporarily
        temp_path = f"/tmp/{job_id}_{file.filename}"
        with open(temp_path, "wb") as f:
            content = await file.read()
            f.write(content)

        # Store job info
        processing_jobs[job_id] = {
            "status": "processing",
            "message": "File processing started",
            "started_at": datetime.now(),
        }

        # Process in background
        import asyncio

        asyncio.create_task(process_file_background(job_id, temp_path, namespace))

        return ProcessResponse(
            job_id=job_id, status="processing", message="File upload and processing started", namespace=namespace
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/process-text", response_model=ProcessResponse)
async def process_text(request: ProcessTextRequest):
    """Process text content directly"""
    try:
        job_id = str(uuid.uuid4())

        # Store job info
        processing_jobs[job_id] = {
            "status": "processing",
            "message": "Text processing started",
            "started_at": datetime.now(),
        }

        # Process in background
        import asyncio

        asyncio.create_task(process_text_background(job_id, request.text_content, request.namespace))

        return ProcessResponse(
            job_id=job_id,
            status="processing",
            message="Text processing started in background",
            namespace=request.namespace,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/parse-text", response_model=ParseTextResponse, responses={200: {"model": ParseTextResponse}})
async def parse_text_sync(request: ProcessTextRequest):
    """Parse text content and extract questions without storing in Chroma.

    Returns a stable JSON payload with the parsed questions and a total count.
    """
    try:
        questions = question_processor.process_text_content(request.text_content)
        return ParseTextResponse(status="success", questions=questions, total=len(questions))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/questions", response_model=QuestionResponse)
async def create_question(question: QuestionCreate):
    """Create a new question manually"""
    try:
        question_data = {
            "id": f"manual_{uuid.uuid4().hex[:8]}",
            "text": question.text,
            "options": question.options,
            "correct_answer": question.correct_answer,
            "subject": question.subject,
            "year": question.year,
            "paper_type": question.paper_type,
            "full_text": f"{question.text} Options: {', '.join(question.options)}",
            "metadata": question.metadata,
        }

        chroma_client.insert_question(question_data)

        return QuestionResponse(
            id=question_data["id"],
            text=question.text,
            options=question.options,
            correct_answer=question.correct_answer,
            subject=question.subject,
            year=question.year,
            paper_type=question.paper_type,
            metadata=question.metadata,
            created_at=datetime.now(),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/questions/batch", response_model=BatchQuestionsResponse)
async def create_questions_batch(request: BatchQuestionsRequest):
    """Create multiple questions in batch"""
    try:
        processed = 0
        errors = []

        for question in request.questions:
            try:
                question_data = {
                    "id": f"batch_{uuid.uuid4().hex[:8]}",
                    "text": question.text,
                    "options": question.options,
                    "correct_answer": question.correct_answer,
                    "subject": question.subject,
                    "year": question.year,
                    "paper_type": question.paper_type,
                    "full_text": f"{question.text} Options: {', '.join(question.options)}",
                    "metadata": question.metadata,
                }

                chroma_client.insert_question(question_data)
                processed += 1
            except Exception as e:
                errors.append(f"Failed to process question: {str(e)}")

        return BatchQuestionsResponse(processed=processed, failed=len(errors), errors=errors)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/subjects", response_model=SubjectsResponse)
async def get_available_subjects():
    """Get list of available subjects"""
    subjects = [
        "General Intelligence and Reasoning",
        "Quantitative Aptitude",
        "English Comprehension",
        "General Awareness",
        "Mathematics",
        "Reasoning",
        "English",
        "GK",
    ]
    return SubjectsResponse(subjects=subjects)


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    try:
        # Check ChromaDB connection
        chroma_client.get_collection_stats()
        db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"

    return HealthResponse(
        status="healthy", service="ssc-rag-api", timestamp=datetime.now(), version="1.0.0", database_status=db_status
    )


@app.get("/stats", response_model=StatsResponse)
async def get_stats():
    """Get system statistics"""
    try:
        total_questions = chroma_client.get_collection_stats()

        # This would require more advanced queries in a real scenario
        subjects_count = {
            "General Intelligence and Reasoning": 0,
            "Quantitative Aptitude": 0,
            "English Comprehension": 0,
            "General Awareness": 0,
        }

        return StatsResponse(
            total_questions=total_questions,
            subjects_count=subjects_count,
            recent_processing={},
            vector_db_status="connected",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/jobs/{job_id}", response_model=ProcessResponse)
async def get_job_status(job_id: str):
    """Get processing job status"""
    if job_id not in processing_jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    job_info = processing_jobs[job_id]
    return ProcessResponse(
        job_id=job_id,
        status=job_info["status"],
        message=job_info["message"],
        questions_processed=job_info.get("questions_processed"),
        namespace=job_info.get("namespace", "ssc-questions"),
    )


# Background task functions
async def process_s3_file_background(job_id: str, bucket: str, key: str, namespace: str):
    """Background task to process S3 file"""
    try:
        # Download from S3
        file_path = s3_client.download_file(bucket, key)

        # Process and upload to ChromaDB
        questions_processed = question_processor.process_and_upload(file_path, namespace)

        processing_jobs[job_id].update(
            {
                "status": "completed",
                "message": f"Successfully processed {questions_processed} questions",
                "questions_processed": questions_processed,
                "completed_at": datetime.now(),
                "namespace": namespace,
            }
        )

        # Cleanup temporary file
        if os.path.exists(file_path):
            os.remove(file_path)

    except Exception as e:
        processing_jobs[job_id].update(
            {"status": "failed", "message": f"Processing failed: {str(e)}", "completed_at": datetime.now()}
        )


async def process_file_background(job_id: str, file_path: str, namespace: str):
    """Background task to process uploaded file"""
    try:
        questions_processed = question_processor.process_and_upload(file_path, namespace)

        processing_jobs[job_id].update(
            {
                "status": "completed",
                "message": f"Successfully processed {questions_processed} questions",
                "questions_processed": questions_processed,
                "completed_at": datetime.now(),
                "namespace": namespace,
            }
        )

        # Cleanup temporary file
        if os.path.exists(file_path):
            os.remove(file_path)

    except Exception as e:
        processing_jobs[job_id].update(
            {"status": "failed", "message": f"Processing failed: {str(e)}", "completed_at": datetime.now()}
        )


async def process_text_background(job_id: str, text_content: str, namespace: str):
    """Background task to process text content"""
    try:
        questions_processed = question_processor.process_text_content(text_content, namespace)

        processing_jobs[job_id].update(
            {
                "status": "completed",
                "message": f"Successfully processed {questions_processed} questions",
                "questions_processed": questions_processed,
                "completed_at": datetime.now(),
                "namespace": namespace,
            }
        )

    except Exception as e:
        processing_jobs[job_id].update(
            {"status": "failed", "message": f"Processing failed: {str(e)}", "completed_at": datetime.now()}
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
