# SurgiScope — Evidence-Grounded Surgical Market Intelligence

SurgiScope is an AI research assistant for analyzing expert interviews about the European robotic surgery market.

It helps researchers:

* Analyze expert interviews against a structured interview guide
* Generate transcript-grounded answers
* Retrieve exact supporting quotes with timestamps
* Compare perspectives across experts and markets
* Identify common themes and differences
* Ask cross-transcript questions
* Clearly indicate when the provided transcripts do not contain sufficient evidence

The system is designed to keep generated insights traceable to the original interview evidence rather than relying on unsupported model knowledge.

## Key Features

### Evidence-Grounded Q&A

Questions are answered using relevant transcript evidence retrieved from the vector database before generation.

### Source Traceability

Each supporting passage retains:

* Expert
* Country / market
* Timestamp
* Speaker
* Source transcript

This allows generated insights to be traced back to the original interview.

### Cross-Expert Insights

SurgiScope synthesizes:

* Common themes
* Differences in expert perspectives
* Market outlook

### Hallucination Reduction

If relevant evidence cannot be retrieved, the system returns:

> Insufficient evidence in the provided transcripts.

The LLM is not called to invent an answer when sufficient supporting evidence is unavailable.

## Architecture

```text
User
  │
  ▼
React + Vite Frontend
  │
  │ REST API
  ▼
FastAPI Backend
  │
  ▼
RAG Pipeline
  │
  ├── Query Embedding
  │
  ▼
ChromaDB
  │
  └── Relevant Transcript Evidence
          │
          ▼
      Gemini LLM
          │
          ▼
Grounded Answer + Evidence
          │
          ├── Expert
          ├── Country
          ├── Timestamp
          └── Source Transcript
```

### Data Ingestion

```text
Expert Transcripts
       │
       ▼
Transcript Parsing
       │
       ├── Expert
       ├── Country
       ├── Speaker
       └── Timestamp
       │
       ▼
Transcript Chunks
       │
       ▼
Gemini Embeddings
       │
       ▼
ChromaDB
```

### Retrieval-Augmented Generation

```text
User Question
      │
      ▼
Query Embedding
      │
      ▼
Semantic Retrieval
      │
      ▼
Relevant Transcript Evidence
      │
      ▼
Grounded Gemini Generation
      │
      ▼
Answer + Source Evidence
```

## Technology Stack

| Layer             | Technology                   |
| ----------------- | ---------------------------- |
| Frontend          | React + Vite                 |
| Backend           | Python + FastAPI             |
| Vector Database   | ChromaDB                     |
| Embeddings        | Gemini Embedding Model       |
| Language Model    | Gemini                       |
| API Communication | REST                         |
| Source Data       | Expert interview transcripts |

## Model Choice

Gemini is used for both embedding generation and grounded response generation.

The embedding model converts transcript content and user questions into vector representations, allowing ChromaDB to retrieve semantically relevant evidence.

The Gemini language model then synthesizes an answer from the retrieved transcript passages.

The application does not rely on the LLM alone to determine source metadata. Expert names, countries, timestamps, speakers, and source filenames are preserved as structured metadata during ingestion.

## Evidence & Hallucination Control

SurgiScope follows an evidence-first approach:

1. The user submits a question.
2. Relevant transcript passages are retrieved.
3. Retrieved evidence is evaluated against a relevance threshold.
4. If sufficient evidence exists, Gemini generates a grounded response.
5. Supporting transcript passages are returned with the answer.
6. If sufficient evidence is unavailable, the application returns an explicit insufficient-evidence response.

This prevents the system from presenting unsupported information as if it came from the interviews.

## Example Research Questions

The application can analyze questions such as:

* What are the main barriers to robotic surgery adoption?
* How important is ROI in hospital purchasing decisions?
* How does surgeon training affect utilization?
* What adoption trends do the experts expect over the next 3–5 years?
* How long does a typical hospital purchasing process take?

It can also answer cross-expert questions such as:

> What do all three experts agree on regarding adoption barriers?

## Project Data

The current case study uses three expert interviews covering:

* France
* Germany
* United Kingdom

The interviews represent different perspectives, including clinical and hospital procurement experience.

The application also uses the provided European Robotic Surgery Market interview guide.

## Running Locally

### 1. Clone the repository

```powershell
git clone https://github.com/minakshi015/SurgiScope-research-intelligence-app.git
cd SurgiScope-research-intelligence-app
```

### 2. Configure the Gemini API key

Create a `.env` file in the project root:

```text
GEMINI_API_KEY=your_gemini_api_key_here
```

Never commit the `.env` file or expose the API key in the frontend.

### 3. Start the backend

```powershell
cd backend
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --port 8001
```

The backend will be available at:

```text
http://127.0.0.1:8001
```

FastAPI documentation:

```text
http://127.0.0.1:8001/docs
```

### 4. Start the frontend

Open a second terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open:

```text
http://localhost:5173
```

## Project Structure

```text
SurgiScope/
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── rag.py
│   │   ├── retrieval.py
│   │   ├── ingestion.py
│   │   ├── embeddings.py
│   │   ├── vector_store.py
│   │   ├── prompts.py
│   │   └── schemas.py
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── App.jsx
│   │   └── index.css
│   └── package.json
│
├── data/
│   ├── Transcript_1_France.txt
│   ├── Transcript_2_Germany.txt
│   ├── Transcript_3_UK.txt
│   └── Interview_Guide.txt
│
├── README.md
├── .env.example
└── .gitignore
```

## Scaling: 3 → 30+ Transcripts

The current implementation is designed around transcript ingestion, metadata preservation, vector retrieval, and grounded generation.

To scale from 3 to 30+ transcripts:

1. Add new transcript files to the ingestion pipeline.
2. Parse and chunk each transcript.
3. Generate embeddings for the new chunks.
4. Store them in the vector database with source metadata.
5. Retrieve only the most relevant evidence for each question.
6. Generate answers from the retrieved evidence rather than loading every transcript into the LLM context.

This keeps the amount of information passed to the language model focused on the evidence relevant to the current question.

For a larger production system, the vector store could be moved to a managed vector database and ingestion could be handled asynchronously.

## Security

* Gemini API keys are stored as environment variables.
* `.env` is excluded from Git.
* API credentials are never stored in frontend source code.
* ChromaDB local data is excluded from Git.

## Case Study

This project was developed as a technical case study for expert-interview analysis and research intelligence.

The design prioritizes:

* Evidence traceability
* Source attribution
* Timestamp preservation
* Cross-expert comparison
* Explicit insufficient-evidence handling
* Simple researcher-focused UX
* Scalable transcript retrieval
