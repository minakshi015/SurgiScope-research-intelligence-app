# SurgiScope — Evidence-Grounded Surgical Market Intelligence

SurgiScope is an AI-powered research assistant for analyzing expert interviews about the **European robotic surgery market**.

The application helps researchers analyze multiple expert interviews, answer structured interview-guide questions, ask custom cross-transcript questions, compare expert perspectives, identify common themes and differences, and trace generated insights back to the original interview evidence.

The system is designed around the principle:

> **Evidence first, generation second.**

Instead of sending complete transcripts directly to a language model, SurgiScope first retrieves and filters relevant evidence from the provided interviews. The selected evidence is then passed to Gemini for grounded response generation.

---

## Table of Contents

* [Problem Statement](#problem-statement)
* [Objective](#objective)
* [Solution Overview](#solution-overview)
* [Key Features](#key-features)
* [Research Scope](#research-scope)
* [Planning and Approach](#planning-and-approach)
* [System Architecture](#system-architecture)
* [RAG Pipeline](#rag-pipeline)
* [Data Ingestion and Indexing](#data-ingestion-and-indexing)
* [Retrieval and Relevance Filtering](#retrieval-and-relevance-filtering)
* [Evidence and Hallucination Control](#evidence-and-hallucination-control)
* [Application Workflow](#application-workflow)
* [Technology Stack](#technology-stack)
* [Project Structure](#project-structure)
* [Requirements](#requirements)
* [Installation](#installation)
* [Environment Configuration](#environment-configuration)
* [Running the Application](#running-the-application)
* [Using the Application](#using-the-application)
* [Example Questions](#example-questions)
* [Unsupported Questions](#unsupported-questions)
* [AI-Assisted Development](#ai-assisted-development)
* [Challenges and Solutions](#challenges-and-solutions)
* [Testing and Validation](#testing-and-validation)
* [Limitations](#limitations)
* [Scaling to 30+ Transcripts](#scaling-to-30-transcripts)
* [Security](#security)
* [Future Improvements](#future-improvements)
* [Core Design Principles](#core-design-principles)
* [Repository](#repository)
* [Author](#author)

---

# Problem Statement

The project focuses on analyzing expert interviews about the **European robotic surgery market**.

The provided research material contains interviews with experts from France, Germany, and the United Kingdom, together with a structured interview guide.

Researchers need to:

* Review multiple interview transcripts
* Find relevant statements
* Answer predefined research questions
* Compare expert perspectives
* Identify common themes
* Identify differences between experts
* Verify answers against the original source

Manually performing these tasks across multiple transcripts can be time-consuming and makes it difficult to quickly trace an insight back to its source.

SurgiScope addresses this by combining semantic retrieval, metadata, relevance filtering, and grounded LLM generation into a single research workflow.

---

# Objective

The main objectives of SurgiScope are to:

1. Answer the predefined interview-guide questions.
2. Allow researchers to ask custom questions.
3. Retrieve relevant evidence from the expert transcripts.
4. Compare perspectives across experts.
5. Identify common themes and differences.
6. Preserve expert and source attribution.
7. Clearly indicate when the available transcripts do not contain sufficient evidence.
8. Reduce unsupported or hallucinated responses.

The application focuses on **traceability and evidence grounding**, rather than generating answers from unrestricted model knowledge.

---

# Solution Overview

SurgiScope uses a Retrieval-Augmented Generation (RAG) architecture.

The overall workflow is:

```text
Expert Transcripts
        ↓
Parsing + Chunking
        ↓
Metadata Preservation
        ↓
Sentence Transformers
all-MiniLM-L6-v2
        ↓
384-dimensional Embeddings
        ↓
ChromaDB
        ↓
User Question
        ↓
Query Embedding
        ↓
Semantic Retrieval
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
        ↓
Answer + Supporting Evidence
```

The key distinction is that **retrieval happens before generation**.

---

# Key Features

## Evidence-Grounded Q&A

Questions are answered using relevant evidence retrieved from the provided transcripts.

The application does not simply provide the complete transcript collection to Gemini.

Instead:

```text
Question
   ↓
Retrieve
   ↓
Filter
   ↓
Select Evidence
   ↓
Generate
```

This makes the final response more traceable to the original research material.

---

## Interview Guide

The Interview Guide contains the six predefined research questions.

The questions cover:

1. Current adoption of robotic surgery in Europe
2. Main barriers to robotic surgery adoption
3. Importance of hospital budgets and ROI
4. Importance of surgeon training and clinical outcomes
5. Expected adoption trend over the next 3–5 years
6. Typical hospital purchasing timeline

For each question, the application retrieves relevant evidence from the expert transcripts.

---

## Ask AI

The Ask AI section allows researchers to ask custom questions about the provided transcripts.

For example:

```text
What are the main barriers to robotic surgery adoption?
```

The question is embedded, relevant evidence is retrieved, topic-specific filtering is applied, and Gemini generates the final response from the selected evidence.

---

## Cross-Expert Insights

The Insights section helps compare the perspectives of the three experts.

It identifies:

* Common themes
* Areas of agreement
* Differences in emphasis
* Expert-specific perspectives
* Areas where estimates differ

The application keeps expert-specific estimates attributed to the respective expert instead of combining them into an unsupported single conclusion.

---

## Evidence Traceability

The retrieved evidence preserves source metadata including:

* Expert
* Country
* Timestamp
* Transcript passage
* Source information

Example:

```text
Expert: Dr. Jean Martin
Country: France
Timestamp: 01:20

Supporting transcript passage...
```

This allows researchers to verify the generated response against the original interview.

---

## Insufficient-Evidence Handling

The application explicitly handles questions that are not supported by the provided transcripts.

When sufficient evidence cannot be found, the application returns:

> **Insufficient evidence in the provided transcripts.**

This prevents the system from presenting unsupported information as if it came from the interview data.

---

# Research Scope

The current case study contains three expert interviews:

| Expert           | Country        |
| ---------------- | -------------- |
| Dr. Jean Martin  | France         |
| Anna Keller      | Germany        |
| Dr. Emily Carter | United Kingdom |

The interviews discuss topics such as:

* Robotic surgery adoption
* Hospital adoption differences
* Financial and capital barriers
* ROI and economics
* Surgeon training
* Clinical outcomes
* Procedure-volume growth
* Hospital purchasing processes
* Future adoption outlook

The application is designed to analyze the information contained in these provided interviews.

It should **not** be interpreted as an independent database representing the complete European robotic surgery market.

---

# Planning and Approach

The system was planned as an evidence-first RAG pipeline.

## Step 1 — Understand the Research Material

The first step was to identify:

* Expert names
* Countries
* Transcript structure
* Timestamps
* Interview questions
* Topics discussed
* Relevant evidence sections

This information is preserved during ingestion.

---

## Step 2 — Parse and Chunk the Transcripts

The transcripts are divided into smaller chunks.

Each chunk retains metadata such as:

```text
Expert
Country
Timestamp
Source File
Transcript Text
```

Preserving this information is important because the application needs to display the origin of retrieved evidence.

---

## Step 3 — Generate Embeddings

Each transcript chunk is converted into a vector representation using:

```text
Sentence Transformers
        ↓
all-MiniLM-L6-v2
        ↓
384-dimensional embedding
```

The same model is used to embed user queries.

This allows transcript passages and questions to be compared using semantic similarity.

---

## Step 4 — Store the Data in ChromaDB

The generated embeddings are stored in ChromaDB together with the original transcript text and metadata.

Conceptually:

```text
ChromaDB
│
├── Embedding
├── Transcript Text
├── Expert
├── Country
├── Timestamp
└── Source File
```

---

## Step 5 — Retrieve Candidate Evidence

When a researcher submits a question, the question is converted into an embedding.

ChromaDB retrieves candidate transcript passages based on semantic similarity.

However, semantic similarity alone is not enough.

A passage may be related to a question without actually answering it.

---

## Step 6 — Classify the Question

The application identifies the main research topic of the question.

The current topic categories are:

```text
Adoption
Barriers
ROI / Economics
Training / Outcomes
Growth Outlook
Purchasing Timeline
```

This allows the retrieval process to apply question-specific filtering.

---

## Step 7 — Apply Relevance Filtering

Retrieved candidates are filtered to identify passages that actually answer the question.

The system follows the principle:

```text
Retrieved
   ≠
Relevant
   ≠
Supported
```

This additional filtering improves retrieval precision compared with relying only on vector similarity.

---

## Step 8 — Select Evidence

The system selects the strongest relevant evidence while preserving expert diversity and source metadata.

The selected evidence contains information such as:

```text
Expert
Country
Timestamp
Quote / Transcript Passage
```

---

## Step 9 — Generate the Response

The selected evidence is passed to Gemini.

Gemini is instructed to:

* Use only the provided evidence
* Avoid inventing facts
* Avoid inventing statistics
* Avoid inventing quotations
* Preserve expert attribution
* Preserve uncertainty
* Avoid unsupported generalizations
* Clearly state when evidence is insufficient

---

## Step 10 — Display the Answer

The final response is displayed in the React frontend together with supporting evidence.

This provides a complete research flow:

```text
Question
   ↓
Evidence
   ↓
Grounded Answer
   ↓
Source Verification
```

---

# System Architecture

The complete architecture is:

```text
                    ┌──────────────────────────┐
                    │   3 Expert Transcripts   │
                    │ France / Germany / UK    │
                    └────────────┬─────────────┘
                                 │
                                 ▼
                     ┌──────────────────────┐
                     │ Transcript Parsing   │
                     │ + Chunking           │
                     └──────────┬───────────┘
                                │
                 ┌──────────────┴──────────────┐
                 │                             │
                 ▼                             ▼
        ┌─────────────────┐          ┌────────────────────┐
        │ Transcript Text │          │ Metadata           │
        │ Smaller chunks  │          │ Expert             │
        │                 │          │ Country            │
        └────────┬────────┘          │ Timestamp          │
                 │                   │ Source file        │
                 ▼                   └──────────┬─────────┘
       ┌────────────────────────┐               │
       │ Sentence Transformers  │               │
       │ all-MiniLM-L6-v2       │               │
       └───────────┬────────────┘               │
                   │ 384-dim embeddings        │
                   ▼                            ▼
              ┌────────────────────────────────────┐
              │              ChromaDB               │
              │ Embedding + Text + Metadata        │
              └────────────────┬───────────────────┘
                               │
                         INDEXING DONE
                               │
═══════════════════════════════╪═══════════════════════════════
                               │
                         USER ASKS QUESTION
                               │
                               ▼
                    ┌──────────────────────┐
                    │    React Frontend    │
                    │      Ask AI          │
                    └──────────┬───────────┘
                               │ HTTP / REST
                               ▼
                    ┌──────────────────────┐
                    │    FastAPI Backend   │
                    └──────────┬───────────┘
                               ▼
                 ┌───────────────────────────┐
                 │ Query Embedding           │
                 │ Sentence Transformers     │
                 └────────────┬──────────────┘
                              ▼
                    ┌──────────────────────┐
                    │       ChromaDB       │
                    │ Semantic Retrieval   │
                    │ Top candidate chunks │
                    └──────────┬───────────┘
                               ▼
                 ┌────────────────────────────┐
                 │    Topic Classification   │
                 │ Adoption / Barriers / ROI │
                 │ Training / Growth / etc. │
                 └────────────┬───────────────┘
                              ▼
                 ┌────────────────────────────┐
                 │ Relevance Filtering        │
                 │ Is this passage actually   │
                 │ answering the question?    │
                 └────────────┬───────────────┘
                              ▼
                 ┌────────────────────────────┐
                 │ Selected Evidence          │
                 │ Expert + Country           │
                 │ Timestamp + Quote          │
                 └────────────┬───────────────┘
                              ▼
                    ┌──────────────────────┐
                    │     Gemini LLM       │
                    │ Grounded Generation  │
                    └──────────┬───────────┘
                               ▼
                    ┌──────────────────────┐
                    │ Final Answer         │
                    │ + Evidence           │
                    │ + Expert             │
                    │ + Timestamp          │
                    └──────────┬───────────┘
                               ▼
                    ┌──────────────────────┐
                    │    React Frontend    │
                    │  Display to User     │
                    └──────────────────────┘
```

---

# RAG Pipeline

The RAG pipeline has two major phases.

## Phase 1 — Indexing

```text
Expert Transcripts
        ↓
Parsing
        ↓
Chunking
        ↓
Metadata Preservation
        ↓
Sentence Transformers
        ↓
all-MiniLM-L6-v2
        ↓
384-dimensional Embeddings
        ↓
ChromaDB
```

The resulting ChromaDB collection contains the transcript evidence required for retrieval.

---

## Phase 2 — Query Processing

```text
User Question
      ↓
Query Embedding
      ↓
ChromaDB Semantic Retrieval
      ↓
Candidate Evidence
      ↓
Topic Classification
      ↓
Question-Specific Relevance Filtering
      ↓
Selected Evidence
      ↓
Gemini
      ↓
Grounded Answer
      ↓
Evidence + Source Metadata
```

---

# Data Ingestion and Indexing

The application begins with the three provided expert transcripts.

Each transcript is parsed into smaller evidence chunks.

For example:

```text
{
    "expert": "Dr. Jean Martin",
    "country": "France",
    "timestamp": "01:20",
    "source": "France transcript",
    "text": "..."
}
```

The transcript text is embedded using:

```text
sentence-transformers/all-MiniLM-L6-v2
```

The model produces:

```text
384-dimensional embeddings
```

These embeddings and associated metadata are stored in ChromaDB.

---

# Retrieval and Relevance Filtering

One of the main technical considerations was improving retrieval precision.

A semantic vector search can retrieve a passage that is conceptually related to a question but does not directly answer it.

For example:

```text
Question:
What is the typical purchasing timeline?

Retrieved passage:
Discussion about robotic surgery adoption.
```

The passage may be semantically related but is not sufficient evidence for the purchasing-timeline question.

Therefore, the application performs:

```text
Semantic Retrieval
        ↓
Topic Classification
        ↓
Question-Specific Filtering
        ↓
Evidence Selection
```

The current retrieval logic handles topics including:

* Adoption
* Barriers
* ROI / Economics
* Training
* Clinical Outcomes
* Growth Outlook
* Purchasing Timeline

---

# Evidence and Hallucination Control

SurgiScope is designed to keep generated answers grounded in the provided interview evidence.

The generation layer is instructed not to:

* Invent facts
* Invent numbers
* Invent statistics
* Invent quotations
* Invent expert opinions
* Invent timestamps
* Introduce unsupported external knowledge
* Treat one expert as representing the entire European market
* Combine different expert estimates into an unsupported single figure

When sufficient evidence cannot be found, the system returns:

```text
Insufficient evidence in the provided transcripts.
```

This provides an explicit boundary between supported research evidence and unavailable information.

---

# Application Workflow

## Interview Guide

The researcher can open the Interview Guide and select one of the six predefined questions.

The application retrieves the relevant transcript evidence and generates an answer.

The researcher can then inspect the evidence associated with the answer.

---

## Ask AI

The researcher can enter a custom question.

For example:

```text
How important are hospital budgets and ROI when adopting robotic surgery?
```

The system processes the question through:

```text
Query Embedding
      ↓
Semantic Retrieval
      ↓
Topic Classification
      ↓
Relevance Filtering
      ↓
Evidence Selection
      ↓
Gemini
```

The final answer is displayed with supporting evidence.

---

## Insights

The Insights section provides cross-expert analysis.

It identifies:

```text
Common Themes
        +
Differences in Perspective
```

The system preserves expert attribution when perspectives or estimates differ.

For example, if different experts provide different growth expectations, the application does not merge those estimates into one unsupported forecast.

---

# Technology Stack

| Layer                     | Technology            |
| ------------------------- | --------------------- |
| Frontend                  | React                 |
| Frontend Tooling          | Vite                  |
| Frontend Language         | JavaScript            |
| Backend                   | Python                |
| API Framework             | FastAPI               |
| Server                    | Uvicorn               |
| Embedding Library         | Sentence Transformers |
| Embedding Model           | `all-MiniLM-L6-v2`    |
| Embedding Dimension       | 384                   |
| Vector Database           | ChromaDB              |
| Generative AI             | Google Gemini         |
| Gemini SDK                | Google GenAI SDK      |
| API Communication         | REST / JSON           |
| Environment Configuration | python-dotenv         |
| Version Control           | Git                   |
| Repository Hosting        | GitHub                |

---

# Technology Details

## React + Vite

React is used to build the interactive research interface.

The frontend contains functionality for:

* Interview Guide
* Ask AI
* Insights
* Answer display
* Evidence display

Vite provides the frontend development and build tooling.

---

## Python + FastAPI

Python is used for the backend and RAG pipeline.

FastAPI provides the REST API layer between the frontend and backend logic.

The backend handles:

* Transcript processing
* Embedding generation
* ChromaDB retrieval
* Topic classification
* Relevance filtering
* Gemini interaction
* Response formatting

---

## Sentence Transformers

The embedding model used by the application is:

```text
sentence-transformers/all-MiniLM-L6-v2
```

It generates:

```text
384-dimensional embeddings
```

The same model is used for:

```text
Transcript chunks
        +
User queries
```

This allows semantic comparison between the research questions and transcript evidence.

---

## ChromaDB

ChromaDB is used as the vector database.

It stores:

* Embeddings
* Transcript text
* Expert metadata
* Country metadata
* Timestamp metadata
* Source metadata

The database performs semantic similarity retrieval for incoming questions.

---

## Google Gemini

Gemini is used for final response generation.

The application does not use Gemini as the transcript embedding model.

Instead:

```text
Sentence Transformers
        ↓
Embedding
        ↓
ChromaDB Retrieval
        ↓
Evidence Filtering
        ↓
Gemini
        ↓
Grounded Response
```

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
│   │
│   └── requirements.txt
│
├── data/
│
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── AskAI.jsx
│   │   │   └── InterviewGuide.jsx
│   │   └── ...
│   │
│   ├── package.json
│   └── ...
│
├── .env.example
├── .gitignore
└── README.md
```

The project structure may evolve as additional application functionality is added.

---

# Requirements

Before running the application, install:

* Python 3.10 or later
* Node.js
* npm
* Git
* Google Gemini API key

The backend dependencies are listed in:

```text
backend/requirements.txt
```

Current Python dependencies include:

```text
fastapi
uvicorn[standard]
chromadb
google-genai
python-dotenv
sentence-transformers
```

---

# Installation

## 1. Clone the Repository

```bash
git clone https://github.com/minakshi015/SurgiScope-research-intelligence-app.git
cd SurgiScope-research-intelligence-app
```

---

## 2. Create the Python Virtual Environment

On Windows PowerShell:

```powershell
python -m venv backend/venv
```

Activate the environment:

```powershell
.\backend\venv\Scripts\Activate.ps1
```

---

## 3. Install Backend Dependencies

```powershell
cd backend
pip install -r requirements.txt
```

---

## 4. Install Frontend Dependencies

Open a separate terminal and run:

```powershell
cd frontend
npm install
```

---

# Environment Configuration

The backend requires a Gemini API key.

Create:

```text
backend/.env
```

Add:

```env
GEMINI_API_KEY=your_gemini_api_key_here
```

The API key is used by the backend and should not be placed in frontend code.

The `.env` file should not be committed to GitHub.

---

# Running the Application

The application consists of two services:

```text
React Frontend
       ↕
FastAPI Backend
```

Both need to be running.

---

## Start the Backend

From the project root:

```powershell
.\backend\venv\Scripts\Activate.ps1
cd backend
uvicorn app.main:app --reload --port 8001
```

Backend:

```text
http://127.0.0.1:8001
```

FastAPI Swagger documentation:

```text
http://127.0.0.1:8001/docs
```

---

## Start the Frontend

Open another terminal:

```powershell
cd frontend
npm run dev
```

Vite will display the local development URL, typically:

```text
http://localhost:5173
```

Open that URL in your browser.

---

# Using the Application

## 1. Start the Backend

```powershell
uvicorn app.main:app --reload --port 8001
```

---

## 2. Start the Frontend

```powershell
npm run dev
```

---

## 3. Open the Application

Open the URL provided by the Vite development server.

---

## 4. Use the Interview Guide

Open the Interview Guide section.

Select one of the six predefined research questions.

The application displays the answer and supporting evidence.

Review the:

* Expert
* Country
* Timestamp
* Supporting transcript passage

---

## 5. Use Ask AI

Open the Ask AI section.

Enter a custom research question.

Example:

```text
What are the main barriers to robotic surgery adoption?
```

The application retrieves relevant evidence and generates the response.

---

## 6. Review Evidence

Inspect the evidence displayed with the answer.

The evidence can be traced back to the corresponding expert transcript and timestamp.

---

## 7. Explore Insights

Open the Insights section to compare the expert perspectives.

The application identifies:

* Common themes
* Differences
* Expert-specific perspectives
* Supporting evidence

---

# Example Questions

### Adoption

```text
What is the current adoption of robotic surgery in Europe?
```

### Barriers

```text
What are the main barriers to robotic surgery adoption?
```

### ROI

```text
How important are hospital budgets and ROI when adopting robotic surgery?
```

### Training

```text
How important are surgeon training and clinical outcomes?
```

### Growth

```text
What is the expected adoption trend over the next 3–5 years?
```

### Purchasing

```text
What is the typical hospital purchasing timeline for robotic surgery?
```

### Cross-Expert Comparison

```text
What do the three experts agree on regarding adoption barriers?
```

```text
How do the experts differ in their expectations for future growth?
```

---

# Unsupported Questions

The application is designed to recognize when information is not available in the provided transcripts.

For example:

```text
What is the population of France?
```

If the transcripts do not contain this information, the system returns:

```text
Insufficient evidence in the provided transcripts.
```

The same behavior applies to unrelated questions or external market information that is not contained in the supplied research material.

---

# AI-Assisted Development

AI tools were used during development of SurgiScope.

AI assistance was used for areas including:

* Code generation
* Code refinement
* Debugging
* Retrieval logic
* Prompt design
* Edge-case handling
* Development guidance

The generated code and suggestions were reviewed, modified, integrated, and tested during implementation.

Gemini is also an intentional component of the application itself and is used for grounded response generation after relevant transcript evidence has been retrieved and filtered.

---

# Challenges and Solutions

## Embedding Quota Limitation

An initial implementation considered Gemini embeddings.

During development, the available Gemini free-tier embedding quota was exhausted, resulting in a quota limitation.

### Solution

Embedding generation was moved to:

```text
Sentence Transformers
all-MiniLM-L6-v2
```

The ChromaDB index was rebuilt using the 384-dimensional embeddings generated by the new model.

This separated embedding generation from Gemini's API quota.

---

## Retrieval Precision

Another challenge was that semantic similarity did not always mean that a passage directly answered the question.

For example, a passage about robotic surgery adoption might be semantically related to a question about purchasing timelines but still not provide the required evidence.

### Solution

The retrieval pipeline was strengthened:

```text
Semantic Retrieval
        ↓
Topic Classification
        ↓
Question-Specific Filtering
        ↓
Evidence Selection
```

This improved the relevance of the evidence passed to the generation layer.

---

## Unsupported Questions

The application needed to avoid generating plausible-sounding answers when the transcripts did not contain the requested information.

### Solution

An explicit insufficient-evidence path was implemented:

```text
No Sufficient Evidence
        ↓
Stop Grounded Generation
        ↓
Insufficient evidence in the provided transcripts.
```

---

## Different Expert Estimates

Experts sometimes provide different estimates or emphasize different factors.

Combining those estimates could create a conclusion that no individual expert actually stated.

### Solution

The system preserves:

* Expert attribution
* Country
* Timestamp
* Supporting passage
* Qualifiers
* Uncertainty

Expert-specific estimates therefore remain associated with the respective expert.

---

# Testing and Validation

The application was tested using supported research questions as well as unsupported questions.

## Supported Questions

Examples:

```text
What are the main barriers to robotic surgery adoption?
```

```text
How important is ROI?
```

```text
How important is surgeon training?
```

```text
What is the growth outlook?
```

```text
What is the hospital purchasing timeline?
```

The retrieved evidence was checked against the relevant transcript sections.

---

## Unsupported Questions

Examples included questions such as:

```text
What is the population of France?
```

and other information not contained in the provided transcripts.

Expected result:

```text
Insufficient evidence in the provided transcripts.
```

---

## Evidence Validation

The predefined questions were checked against their expected evidence topics:

| Topic               | Evidence Focus                                          |
| ------------------- | ------------------------------------------------------- |
| Adoption            | Current adoption and differences between hospital types |
| Barriers            | Capital, cost, funding and utilization barriers         |
| ROI / Economics     | Utilization, maintenance, procedure volume and cost     |
| Training / Outcomes | Training capacity and clinical outcomes                 |
| Growth              | Expert-specific future growth expectations              |
| Purchasing Timeline | Procurement and capital-budget timelines                |

---

# Limitations

## Limited Source Dataset

The current implementation uses three expert transcripts.

It does not represent the complete European robotic surgery market.

---

## No External Market Validation

The application does not independently validate interview statements against external:

* Market databases
* Government datasets
* Company reports
* Industry reports
* External research databases

The current system is intentionally grounded in the provided transcripts.

---

## No Large-Scale Benchmark

The current implementation has not been benchmarked on a 30+ transcript dataset.

Therefore, no large-scale performance claims are made.

---

## Local Vector Database

The current implementation uses ChromaDB locally.

A production system with a substantially larger dataset may require a managed vector database or other scalable storage solution.

---

# Scaling to 30+ Transcripts

The same core RAG architecture can be extended to a larger transcript collection.

A scaled ingestion workflow could be:

```text
New Transcripts
       ↓
Automated Ingestion
       ↓
Parsing + Chunking
       ↓
Metadata Extraction
       ↓
Batch Embedding
       ↓
Vector Database
       ↓
Metadata Filtering
       ↓
Semantic Retrieval
       ↓
Relevance Filtering
       ↓
Grounded Generation
```

Potential improvements include:

* Automated transcript ingestion
* Batch embedding generation
* Structured metadata extraction
* Metadata-based pre-filtering
* Efficient top-k retrieval
* Retrieval evaluation
* Response evaluation
* Monitoring
* Managed vector database deployment

These are future scaling considerations and have not been benchmarked in the current implementation.

---

# Security

## API Key Protection

The Gemini API key is stored in an environment variable:

```env
GEMINI_API_KEY=your_api_key_here
```

It is not placed in the frontend source code.

---

## Git Protection

Sensitive environment files should not be committed.

The `.gitignore` configuration excludes local environment files and generated local data.

Never commit:

```text
.env
API keys
Secret tokens
Credentials
```

---

# Future Improvements

## Larger Dataset Support

Extend the ingestion pipeline to support dozens or hundreds of expert transcripts.

---

## Automated Transcript Upload

Allow researchers to upload new transcript files and automatically:

```text
Upload
  ↓
Parse
  ↓
Chunk
  ↓
Embed
  ↓
Index
```

---

## Advanced Metadata Filtering

Support filtering by:

* Country
* Expert
* Interview
* Topic
* Date
* Source

---

## Retrieval Evaluation

Introduce a formal evaluation dataset to measure:

* Retrieval precision
* Retrieval recall
* Evidence coverage
* Answer faithfulness
* Unsupported-answer rate

---

## Production Vector Database

For larger datasets, move from local ChromaDB to a production-ready vector database architecture.

---

## Research Export

Add the ability to export:

* Answers
* Evidence
* Expert comparisons
* Insights

into structured research reports.

---

# Core Design Principles

## Evidence First

Relevant evidence is retrieved before response generation.

## Source Traceability

Expert, country, timestamp, and source information remain attached to retrieved evidence.

## Expert Attribution

Expert-specific claims remain attributed to the relevant expert.

## No Unsupported Generation

When sufficient evidence is unavailable, the system explicitly states that.

## Retrieval Before Generation

The LLM is used after the evidence retrieval and filtering stages rather than being asked to independently answer from unrestricted knowledge.

---

# Repository

GitHub:

https://github.com/minakshi015/SurgiScope-research-intelligence-app

---

# Author

**Minakshi Ghodella**

B.E. Artificial Intelligence & Data Science

Pune, Maharashtra, India

---

## Core Architecture Summary

```text
                 SURGISCOPE
                     │
                     ▼
          ┌─────────────────────┐
          │ Expert Transcripts  │
          └──────────┬──────────┘
                     ↓
              Parsing + Chunking
                     ↓
          Sentence Transformers
             all-MiniLM-L6-v2
                     ↓
             384-D Embeddings
                     ↓
                 ChromaDB
                     │
                     │
              ───── QUERY ─────
                     │
                     ↓
              User Question
                     ↓
              Query Embedding
                     ↓
            Semantic Retrieval
                     ↓
            Topic Classification
                     ↓
            Relevance Filtering
                     ↓
            Selected Evidence
                     ↓
             Google Gemini
                     ↓
          Grounded Final Answer
                     ↓
       Answer + Expert + Timestamp
                     ↓
              React Frontend
```

> **SurgiScope — Evidence first, generation second.**
