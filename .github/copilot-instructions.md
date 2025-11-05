## Quick context

This repository implements a small RAG (retrieval-augmented generation) system for SSC exam questions.
Major components:
- backend (FastAPI) — source: `backend/app/main.py`, `backend/app/*.py`
- vector DB (ChromaDB) — client wrapper: `backend/app/chroma_client.py`
- PDF/question extraction — `backend/app/question_processor.py`
- frontend (React + Vite) — `frontend/src/*` and `frontend/package.json`

Keep this file short — the goal is to help an AI coding agent become productive quickly.

## Big picture / architecture notes
- FastAPI app lives in `backend/app/main.py`. The app wires three main helpers: `S3Client` (`backend/app/s3_client.py`), `ChromaClient` (`backend/app/chroma_client.py`) and `QuestionProcessor` (`backend/app/question_processor.py`).
- ChromaDB runs as a container in docker-compose and the code uses either a PersistentClient on-disk (`chroma_db` folder) or optionally an HTTP client. See `backend/docker-compose-backend.yml` and top-level `docker-compose.yml` (service `chromadb`).
- Question ingestion flows: uploaded PDF -> `QuestionProcessor` extracts questions via regex heuristics -> `ChromaClient.batch_insert_questions` creates embeddings with a SentenceTransformer model and stores documents/metadatas in ChromaDB.
- Runtime job handling is currently in-process: background jobs are tracked in the module-level `processing_jobs` dict (in `main.py`). This is a simple in-memory job registry — production should replace with Redis/DB (redis service is optional in compose).

## Important files to read first
- `backend/app/main.py` — API endpoints, background task entrypoints, job tracking.
- `backend/app/question_processor.py` — PDF parsing heuristics (uses PyPDF2 + regex). Good for improving extraction accuracy.
- `backend/app/chroma_client.py` — embedding generation (SentenceTransformer), insertion and query code. Shows the metadata shape the frontend expects.
- `backend/.env.example` and `backend/docker-compose-backend.yml` — essential dev/runtime env vars and Docker config.
- `backend/Dockerfile` — NOTE: Dockerfile currently runs `python run.py` but there is no `run.py` at the repo root; the FastAPI app is in `backend/app/main.py`. See "quirks" below.

## How to run locally (developer workflows)
- Full stack (recommended): from repo root
```powershell
cp backend/.env.example backend/.env; docker-compose up -d
```
This composes `backend`, `frontend` and `chromadb` services (top-level `docker-compose.yml`).

- Backend only (docker-compose):
```powershell
cd backend
cp .env.example .env
docker-compose -f docker-compose-backend.yml up --build
```

- Backend only (fast, dev without Docker): run Uvicorn directly (the app object is `app` in `backend/app/main.py`):
```powershell
cd backend
# Install deps into a venv, then:
python -m pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

- Frontend (dev):
```powershell
cd frontend
npm install
npm run dev
```

## Patterns & conventions specific to this repo
- Background work: lightweight in-memory job registry `processing_jobs` (key: job_id) returned by `/process-file`, `/process-text`, `/process-s3-file`. Expect to see `get_job_status` endpoint in `main.py`.
- Embedding / metadata shape: `ChromaClient` stores `full_text` as the document and `metadatas` containing `text`, `options`, `correct_answer`, `subject`, `question_id`. When adding code that reads results, follow this metadata layout.
- Question IDs: generated strings like `q_<md5...>` (see `question_processor.py`) — don't assume numeric ids.
- PDF parsing heuristics live in `_split_into_question_blocks` and `_parse_question_block`. Changes to question extraction should be validated by running `QuestionProcessor.process_text_content(sample_text)` as a quick smoke test.

## Integration points & external dependencies
- ChromaDB: local container mapped to host port `8001:8000` in the compose. The code uses `chromadb.PersistentClient(path="./chroma_db")` by default. To switch to HTTP-based Chroma server, use the HttpClient variant in `chroma_client.py`.
- SentenceTransformer model: `all-MiniLM-L6-v2` is downloaded at startup by `ChromaClient` — heavy network/IO on first run.
- S3 interactions are abstracted in `backend/app/s3_client.py` (Boto3). The backend expects AWS env vars: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_REGION`.

## Quirks & gotchas discovered (actionable)
- Dockerfile vs code mismatch: `backend/Dockerfile` ends with `CMD ["python", "run.py"]`, but there is no `run.py` at `backend/` or repo root. Building the backend image will fail unless you either:
  - add a `run.py` that imports and runs `uvicorn app.main:app`, or
  - change the Dockerfile CMD to `uvicorn app.main:app --host 0.0.0.0 --port 8000`.
Agents should highlight and optionally propose a small patch when opening PRs.

- No persistent job queue: any long-running ingestion will be lost if the container restarts. For production, use Redis and move `processing_jobs` state out of process.

## Useful quick code examples for agents
- Start a local semantic query (from python REPL inside `backend` venv):
```python
from app.chroma_client import ChromaClient
cc = ChromaClient()
print(cc.semantic_search("profit and loss", top_k=3))
```

- Run a quick parsing test (prints parsed questions):
```python
from app.question_processor import create_question_processor
proc = create_question_processor()
proc.process_text_content("Section : Quantitative\nQ.1 What is 2+2?\n1. 3\n2. 4\nAns 2")
```

## What to do first when contributing
1. Read `backend/app/main.py`, then `backend/app/chroma_client.py` and `backend/app/question_processor.py`.
2. Reproduce: run backend + chroma (use `docker-compose -f backend/docker-compose-backend.yml up`) or run uvicorn locally.
3. If you plan to change container startup, fix `backend/Dockerfile` to use `uvicorn app.main:app` or add `run.py`.

---
If any of these points are unclear, tell me which area you'd like expanded (startup, ingestion, Chroma usage, or Dockerfile fix) and I'll iterate. 
