# SurgiScope — Evidence-Grounded Surgical Market Intelligence

SurgiScope is an AI-powered research application for analyzing expert interviews about the **European robotic surgery market**.

It helps researchers:

* Analyze expert interviews using a structured interview guide
* Generate answers grounded in transcript evidence
* Retrieve supporting quotes with expert, country, and timestamp
* Compare perspectives across experts
* Identify common themes and differences
* Ask custom questions across transcripts
* Indicate when the provided transcripts do not contain sufficient evidence

The system follows an **evidence-first approach**: relevant transcript evidence is retrieved and filtered before Gemini generates the final response.

---

## Key Features

### 1. Interview Guide

Provides answers to the six predefined research questions covering:

* Current robotic surgery adoption
* Barriers to adoption
* Hospital budgets and ROI
* Surgeon training and clinical outcomes
* 3–5 year adoption outlook
* Hospital purchasing timelines

Each answer is supported by relevant expert evidence.

### 2. Ask AI

Allows researchers to ask custom questions about the provided transcripts.

The system retrieves relevant evidence, identifies the question topic, filters the evidence, and generates a grounded response.

### 3. Cross-Expert Insights

Identifies:

* Common themes across experts
* Differences in perspectives
* Expert-specific estimates and viewpoints

Different expert estimates are kept attributed to the respective expert rather than being combined into one unsupported conclusion.

### 4. Evidence Traceability

Responses can be traced back to the original interview evidence through:

* Expert
* Country
* Timestamp
* Transcript passage

### 5. Insufficient-Evidence Handling

If the provided transcripts do not contain enough information to answer a question, the system returns:

> **Insufficient evidence in the provided transcripts.**

This prevents unsupported information from being presented as transcript evidence.

---

# Research Scope

The current application analyzes three expert interviews:

| Expert           | Country        |
| ---------------- | -------------- |
| Dr. Jean Martin  | France         |
| Anna Keller      | Germany        |
| Dr. Emily Carter | United Kingdom |

The interviews cover topics including robotic surgery adoption, barriers, economics and ROI, training, clinical outcomes, growth expectations, and purchasing timelines.

The application is designed to analyze the **provided interview data**, rather than independently represent the complete European robotic surgery market.

---

# Planning & Approach

The system was designed as a Retrieval-Augmented Generation (RAG) pipeline.

### 1. Transcript Processing

The three transcripts are parsed and divided into smaller chunks.

Important metadata is preserved with each chunk:

```text
Expert
Country
Timestamp
Source
Transcript Text
```

### 2. Embedding Generation

Transcript chunks are converted into embeddings using:

```text
Sentence Transformers
all-MiniLM-L6-v2
```

The model produces **384-dimensional embeddings**.

### 3. Vector Storage

Embeddings, transcript text, and metadata are stored in **ChromaDB**.

### 4. Question Processing

When a researcher asks a question:

```text
User Question
      ↓
Query Embedding
      ↓
ChromaDB Retrieval
      ↓
Topic Classification
      ↓
Relevance Filtering
      ↓
Selected Evidence
      ↓
Gemini
      ↓
Grounded Answer
```

### 5. Grounded Generation

Only the selected transcript evidence is provided to Gemini for response generation.

The generation process is instructed to:

* Use only the provided evidence
* Preserve expert attribution
* Preserve uncertainty
* Avoid inventing facts, numbers, quotes, or sources
* Return insufficient evidence when appropriate

---

# System Architecture

```text
┌──────────────────────────┐ │ 3 Expert Transcripts │ │ France / Germany / UK │ └────────────┬─────────────┘ │ ▼ ┌──────────────────────────┐ │ Transcript Parsing │ │ + Chunking │ └────────────┬─────────────┘ │ ┌────────────┴────────────┐ │ │ ▼ ▼ ┌──────────────────┐ ┌────────────────────┐ │ Transcript Text │ │ Metadata │ │ Smaller Chunks │ │ Expert │ │ │ │ Country │ └────────┬─────────┘ │ Timestamp │ │ │ Source File │ │ └──────────┬─────────┘ ▼ │ ┌──────────────────────┐ │ │ Sentence Transformers│ │ │ all-MiniLM-L6-v2 │ │ └──────────┬───────────┘ │ │ 384-dim Embeddings │ └──────────────┬───────────┘ │ ▼ ┌─────────────────────┐ │ ChromaDB │ │ │ │ Embeddings │ │ Transcript Text │ │ Metadata │ └──────────┬──────────┘ │ INDEXING COMPLETE │ ════════════════════════════════════╪════════════════════════════════════ │ ┌──────────┴──────────┐ │ │ │ QUERY PIPELINE │ │ │ ▼ │ ┌──────────────────────┐ │ │ React Frontend │ │ │ Interview Guide │ │ │ Ask AI / Insights │ │ └──────────┬───────────┘ │ │ HTTP / REST │ ▼ │ ┌──────────────────────┐ │ │ FastAPI Backend │ │ └──────────┬───────────┘ │ ▼ │ ┌──────────────────────┐ │ │ Query Embedding │ │ │ Sentence Transformers│ │ └──────────┬───────────┘ │ │ │ └─────────┐ │ ▼ │ ┌─────────────┐ │ │ ChromaDB │◄──┘ │ Retrieval │ └──────┬──────┘ ▼ ┌─────────────────────┐ │ Topic Classification│ │ │ │ Adoption │ │ Barriers │ │ ROI / Economics │ │ Training / Outcomes │ │ Growth │ │ Purchasing Timeline │ └──────────┬──────────┘ ▼ ┌─────────────────────┐ │ Relevance Filtering │ │ │ │ Is the passage │ │ actually answering │ │ the question? │ └──────────┬──────────┘ ▼ ┌─────────────────────┐ │ Selected Evidence │ │ │ │ Expert │ │ Country │ │ Timestamp │ │ Transcript Passage │ └──────────┬──────────┘ ▼ ┌─────────────────────┐ │ Google Gemini │ │ Grounded Generation │ └──────────┬──────────┘ ▼ ┌─────────────────────┐ │ Final Answer │ │ + Evidence │ │ + Source Info │ └──────────┬──────────┘ ▼ ┌─────────────────────┐ │ React Frontend │ │ Display Result │ └─────────────────────┘
```

---

# Technology Stack

| Component       | Technology              |
| --------------- | ----------------------- |
| Frontend        | React, Vite, JavaScript |
| Backend         | Python, FastAPI         |
| Server          | Uvicorn                 |
| Embeddings      | Sentence Transformers   |
| Embedding Model | `all-MiniLM-L6-v2`      |
| Vector Database | ChromaDB                |
| Generative AI   | Google Gemini           |
| AI SDK          | Google GenAI SDK        |
| API             | REST / JSON             |
| Configuration   | python-dotenv           |
| Version Control | Git, GitHub             |

---

# Project Structure

```text
SurgiScope-research-intelligence-app/
│
├── backend/
│   ├── app/
│   │   ├── embeddings.py
│   │   ├── main.py
│   │   └── prompts.py
│   └── requirements.txt
│
├── data/
│   └── transcripts / research data
│
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── AskAI.jsx
│   │   │   └── InterviewGuide.jsx
│   │   └── ...
│   └── package.json
│
├── .env.example
├── .gitignore
└── README.md
```

---

# Requirements

Before running the application, install:

* Python 3.10+
* Node.js
* npm
* Git
* Google Gemini API key

---

# Installation & Setup

## 1. Clone the Repository

```bash
git clone https://github.com/minakshi015/SurgiScope-research-intelligence-app.git
cd SurgiScope-research-intelligence-app
```

## 2. Create Python Virtual Environment

### Windows PowerShell

```powershell
python -m venv backend/venv
.\backend\venv\Scripts\Activate.ps1
```

## 3. Install Backend Dependencies

```powershell
cd backend
pip install -r requirements.txt
```

## 4. Install Frontend Dependencies

Open another terminal:

```powershell
cd frontend
npm install
```

---

# Environment Configuration

Create:

```text
backend/.env
```

Add your Gemini API key:

```env
GEMINI_API_KEY=your_gemini_api_key_here
```

The API key is used only by the backend and should not be exposed in frontend code.

Do not commit `.env` to GitHub.

---

# Running the Application

The backend and frontend run separately.

## Start Backend

```powershell
.\backend\venv\Scripts\Activate.ps1
cd backend
uvicorn app.main:app --reload --port 8001
```

Backend:

```text
http://127.0.0.1:8001
```

FastAPI documentation:

```text
http://127.0.0.1:8001/docs
```

## Start Frontend

Open a second terminal:

```powershell
cd frontend
npm run dev
```

Open the local URL displayed by Vite, usually:

```text
http://localhost:5173
```

---

# Using the Application

### Interview Guide

Select one of the predefined research questions to view the generated answer and supporting evidence.

### Ask AI

Enter a custom question related to the provided expert interviews.

Example:

```text
What are the main barriers to robotic surgery adoption?
```

The system retrieves and filters relevant evidence before generating the answer.

### Insights

View common themes and differences across the three expert perspectives.

### Evidence

Review the expert, country, timestamp, and transcript passage supporting the response.

---

# Example Questions

```text
What is the current adoption of robotic surgery in Europe?
```

```text
What are the main barriers to robotic surgery adoption?
```

```text
How important are hospital budgets and ROI?
```

```text
How important are surgeon training and clinical outcomes?
```

```text
What is the expected adoption trend over the next 3–5 years?
```

```text
What is the typical hospital purchasing timeline?
```

Cross-expert example:

```text
How do the experts differ in their expectations for future growth?
```

---

# Unsupported Questions

If the requested information is not available in the provided transcripts, the application does not generate an unsupported response.

For example:

```text
What is the population of France?
```

Result:

```text
Insufficient evidence in the provided transcripts.
```

---

# AI-Assisted Development

AI tools were used during development for:

* Code generation and refinement
* Debugging
* Retrieval logic
* Prompt design
* Edge-case handling

The AI-assisted implementation was reviewed, modified, and tested against the provided transcripts.

Within the application, **Google Gemini** is used for grounded response generation after relevant evidence has been retrieved and filtered.

---

# Challenges & Solutions

### 1. Embedding Quota

The initial embedding approach using Gemini embeddings encountered a free-tier quota limitation.

**Solution:** switched embedding generation to the local `all-MiniLM-L6-v2` model and rebuilt the ChromaDB index.

### 2. Retrieval Precision

Semantic similarity sometimes returned passages that were related but did not directly answer the question.

**Solution:** added topic classification and question-specific relevance filtering.

### 3. Unsupported Information

The system needed to avoid generating answers when the transcripts did not contain sufficient evidence.

**Solution:** implemented an explicit insufficient-evidence path.

### 4. Different Expert Perspectives

Experts sometimes provided different estimates or emphasized different factors.

**Solution:** preserve expert attribution, timestamps, and supporting passages rather than combining different estimates into one unsupported conclusion.

---

# Testing

The application was tested using:

### Supported Questions

* Adoption
* Barriers
* ROI / Economics
* Training / Outcomes
* Growth Outlook
* Purchasing Timeline

### Unsupported Questions

Questions involving information not contained in the transcripts were tested to verify that the system returns:

```text
Insufficient evidence in the provided transcripts.
```

The retrieved evidence for the predefined interview questions was also checked against the corresponding transcript sections.

---

# Limitations

* The current dataset contains three expert transcripts.
* The application is focused on the provided research material.
* It does not independently validate claims using external market databases.
* Expert estimates remain attributed to individual experts.
* The system has not been benchmarked on a 30+ transcript dataset.
* The current vector database is local ChromaDB.

---

# Future Scaling

For a larger collection of 30+ transcripts, the same RAG architecture can be extended with:

* Automated transcript ingestion
* Batch embedding generation
* Metadata-based filtering
* Larger-scale retrieval evaluation
* Efficient vector storage
* Retrieval and answer evaluation
* Production vector database deployment

The current implementation demonstrates the architecture using the provided three transcripts.

---

# Core Design Principle

> **Evidence first, generation second.**

SurgiScope retrieves and filters relevant evidence from the provided expert interviews before using Gemini to generate the final response.

This keeps the research output **traceable, source-aware, and explicit about insufficient evidence**.

---

## Repository

**GitHub:**
https://github.com/minakshi015/SurgiScope-research-intelligence-app

## Author

**Minakshi Ghodella**
B.E. Artificial Intelligence & Data Science
