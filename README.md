 # SurgiScope — Evidence-Grounded Surgical Market Intelligence

SurgiScope is an AI research assistant for analyzing expert interviews about
the European robotic surgery market. It provides transcript-grounded answers,
interview-guide analysis, and cross-expert insights with source-linked
evidence.

## Architecture

- Frontend: React + Vite
- Backend: Python + FastAPI
- Vector database: ChromaDB
- Embeddings: Gemini embedding model
- Language model: Gemini
- Source data: expert interview transcripts in `data/`

The frontend communicates with the FastAPI backend at
`http://127.0.0.1:8000` during local development.

## Run locally

Start the backend:

```powershell
cd backend
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --reload
```

Start the frontend in a second terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173` in a browser.

The Gemini API key remains in the project `.env` file as
`GEMINI_API_KEY` and is used only by the backend.
