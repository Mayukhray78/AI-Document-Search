[![Project CI](https://github.com/Mayukhray78/AI-Document-Search/actions/workflows/ci.yml/badge.svg)](https://github.com/Mayukhray78/AI-Document-Search/actions/workflows/ci.yml)

# AI Document Search Platform

A full-stack Retrieval-Augmented Generation (RAG) application that allows users to securely upload PDF documents and ask questions based on their contents.

The platform extracts and divides PDF text into chunks, generates semantic embeddings, stores them in Qdrant, retrieves relevant context, and uses the Hugging Face Qwen3-8B model to generate context-grounded answers.

## Features

- User registration and login
- JWT-based authentication
- Secure password hashing
- User-specific document access
- PDF type and size validation
- PDF text extraction and chunking
- 384-dimensional semantic embeddings
- Qdrant cosine-similarity search
- Context-grounded AI answers
- Document listing and deletion
- Responsive React and TypeScript interface
- Automated backend and frontend CI
- Unit and API tests

## Technology Stack

### Backend

- Python 3.12
- FastAPI
- SQLAlchemy
- PostgreSQL
- Pydantic
- JWT authentication
- Passlib and bcrypt

### AI and RAG

- Sentence Transformers
- Qdrant
- PyMuPDF
- LangChain Text Splitters
- Hugging Face Inference API
- Qwen3-8B

### Frontend

- React
- TypeScript
- Vite
- Axios
- React Router
- CSS

### Development and Testing

- Pytest
- FastAPI TestClient
- Git and GitHub
- GitHub Actions

## Architecture

```mermaid
flowchart TD
    U[User] --> F[React Frontend]
    F --> A[FastAPI REST API]
    A --> P[(PostgreSQL)]
    A --> E[PDF Processing]
    E --> M[Sentence Transformer]
    M --> Q[(Qdrant)]
    A --> R[Semantic Retrieval]
    Q --> R
    R --> H[Hugging Face Qwen3-8B]
    H --> A
    A --> F
```

## RAG Workflow

1. The user registers and logs in.
2. The backend generates a JWT access token.
3. The authenticated user uploads a PDF.
4. PyMuPDF extracts text from the document.
5. The text is divided into smaller chunks.
6. Sentence Transformers generate embeddings.
7. Qdrant stores the embeddings and document metadata.
8. The user submits a question.
9. The question is converted into an embedding.
10. Qdrant retrieves the most relevant chunks.
11. The question and retrieved context are sent to Qwen3-8B.
12. The generated answer is returned to the frontend.

## Project Structure

```text
AI-Document-Search/
├── .github/
│   └── workflows/
│       └── ci.yml
├── app/
│   ├── ai/
│   ├── api/
│   ├── core/
│   ├── db/
│   ├── models/
│   ├── repositories/
│   ├── schemas/
│   ├── services/
│   └── main.py
├── frontend/
│   ├── public/
│   ├── src/
│   └── package.json
├── tests/
├── uploads/
├── .env.example
├── .gitignore
├── pytest.ini
├── requirements.txt
└── README.md
```

## Prerequisites

Install the following software:

- Python 3.12
- Node.js 20 or later
- PostgreSQL
- Qdrant
- Git

A Hugging Face account and access token are required for answer generation.

## Environment Configuration

Create a `.env` file in the project root.

Use `.env.example` as the template:

```env
DATABASE_URL=postgresql://postgres:your_password@localhost:5433/ai_document_search
QDRANT_URL=http://localhost:6333
HF_TOKEN=your_hugging_face_token
SECRET_KEY=your_secret_key
```

Never commit the `.env` file or real credentials to GitHub.

## Backend Setup

Clone the repository:

```bash
git clone https://github.com/Mayukhray78/AI-Document-Search.git
cd AI-Document-Search
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

Create the PostgreSQL database:

```sql
CREATE DATABASE ai_document_search;
```

Start Qdrant and ensure it is available at:

```text
http://localhost:6333
```

Start the backend:

```bash
uvicorn app.main:app --reload
```

The backend will be available at:

```text
http://127.0.0.1:8000
```

Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

## Frontend Setup

Open another terminal:

```bash
cd frontend
npm install
npm run dev
```

The frontend will be available at:

```text
http://localhost:5173
```

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Application status |
| `GET` | `/health` | Backend health check |
| `POST` | `/auth/register` | Register a user |
| `POST` | `/auth/login` | Log in and receive a JWT |
| `POST` | `/documents/upload` | Upload and index a PDF |
| `GET` | `/documents/` | List the user's documents |
| `DELETE` | `/documents/{document_id}` | Delete a document |
| `POST` | `/rag/ask` | Ask a document-based question |

Protected endpoints require:

```text
Authorization: Bearer <access_token>
```

## Running Tests

Run all backend tests:

```bash
python -m pytest -v
```

The test suite covers:

- Password hashing and verification
- JWT creation
- User schema validation
- Application health endpoints
- Registration and login
- Invalid authentication
- Protected document access
- Missing-document deletion

## Continuous Integration

GitHub Actions runs automatically for every push and pull request to `main`.

The workflow performs:

### Backend checks

- Installs Python dependencies
- Configures an isolated SQLite test database
- Runs the Pytest test suite

### Frontend checks

- Installs Node.js dependencies
- Runs ESLint
- Creates a production frontend build

The CI badge at the top of this README displays the current workflow status.

## Security

- Passwords are stored as secure hashes.
- Authentication uses expiring JWT access tokens.
- Documents are isolated by user ownership.
- Uploaded files are validated by extension, MIME type, and size.
- Stored filenames use generated UUID values.
- Secrets are loaded from environment variables.
- The `.env` file, uploaded PDFs, local databases, and generated files are excluded from Git.

## Current Limitations

- Uploaded files are stored on the local filesystem.
- PostgreSQL and Qdrant must be started separately.
- Hugging Face inference depends on provider availability and usage limits.
- Scanned PDFs require OCR support, which is not currently included.

## Future Improvements

- Cloud deployment
- Automated CD pipeline
- Object storage for uploaded documents
- OCR support for scanned PDFs
- Document citations with page numbers
- Streaming AI responses
- Rate limiting
- Refresh tokens
- Password reset and email verification
- Expanded integration and RAG evaluation tests

## Author

**Mayukh Ray**

- GitHub: [Mayukhray78](https://github.com/Mayukhray78)