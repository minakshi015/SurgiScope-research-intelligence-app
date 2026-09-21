from fastapi import FastAPI
import json
from pathlib import Path
from fastapi.middleware.cors import CORSMiddleware

from app.ingestion import load_all_transcripts
from app.vector_store import index_transcripts, search_transcripts
from app.rag import generate_grounded_answer, generate_insights
from app.prompts import (
    INTERVIEW_GUIDE,
    build_expert_guide_prompt,
)


app = FastAPI(
    title="Hasamex Research AI",
    description="AI-powered analysis of expert interview transcripts",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MAX_EVIDENCE_DISTANCE = 0.175

GUIDE_RELEVANCE_TERMS = {
    1: (
        "adoption", "growing", "concentrated", "academic", "university",
        "private", "nhs", "hospital", "hospitals", "regional", "access",
        "uneven", "advanced", "waiting", "standard", "selected",
    ),
    2: (
        "barrier", "cost", "capital", "budget", "funding", "finance",
        "utilisation", "utilization", "training", "trained", "procedure",
        "volume", "economic", "sustainable",
    ),
    3: (
        "roi", "capital", "budget", "procedure", "volume", "utilisation",
        "utilization", "maintenance", "pay", "cost", "economic", "finance",
        "business case", "investment",
    ),
    4: (
        "training", "trained", "surgeon", "surgeons", "theatre", "staff",
        "outcomes", "clinical", "utilisation", "utilization", "procedure",
    ),
    5: (
        "expect", "expected", "outlook", "growth", "growing", "increase",
        "increasing", "accelerate", "acceleration", "annual", "years", "future",
    ),
    6: (
        "month", "months", "purchase", "purchasing", "procurement", "timeline",
        "capital", "committee", "budget", "cycle", "management", "align",
    ),
}

INSIGHTS_RETRIEVAL_QUERIES = (
    "current robotic surgery adoption uneven hospital access",
    "capital budgets ROI utilization training economic barriers",
    "future adoption growth procedure volumes cost competitiveness",
    "hospital purchasing timeline procurement budget cycle",
)

@app.get("/")
def root():
    return {
        "message": "Hasamex Research AI backend is running"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }


@app.get("/transcripts")
def get_transcripts():
    transcripts = load_all_transcripts()

    return {
        "count": len(transcripts),
        "transcripts": [
            {
                "expert": transcript["expert"],
                "role": transcript["role"],
                "country": transcript["country"],
                "source": transcript["source"],
                "segment_count": len(transcript["segments"]),
            }
            for transcript in transcripts
        ],
    }
    
@app.get("/transcripts/{country}")
def get_transcript_segments(country: str):
    transcripts = load_all_transcripts()

    for transcript in transcripts:
        if transcript["country"].lower() == country.lower():
            return {
                "expert": transcript["expert"],
                "role": transcript["role"],
                "country": transcript["country"],
                "source": transcript["source"],
                "segments": transcript["segments"],
            }

    return {
        "error": f"No transcript found for {country}"
    }
    
@app.post("/index")
def index_all_transcripts():
    transcripts = load_all_transcripts()

    count = index_transcripts(transcripts)

    return {
        "message": "Transcripts indexed successfully",
        "segments_indexed": count,
    }

@app.get("/search")
def search_transcript_evidence(
    query: str,
    n_results: int = 5,
):
    results = search_transcripts(query, n_results)

    return {
        "query": query,
        "results": results,
    }
    
@app.get("/ask")
def ask_question(
    query: str,
    n_results: int = 6,
):
    evidence = search_transcripts(query, n_results)

    if (
        not evidence
        or evidence[0].get("distance", float("inf"))
        > MAX_EVIDENCE_DISTANCE
    ):
        evidence = []

    if evidence:
        generated = generate_grounded_answer(
            question=query,
            evidence=evidence,
        )
        answer = generated["answer"]
        perspective = generated["perspective"]
        evidence_status = "Supported"
    else:
        answer = "Insufficient evidence in the provided transcripts."
        perspective = []
        evidence_status = "Insufficient evidence"

    return {
        "query": query,
        "answer": answer,
        "perspective": perspective,
        "evidence": evidence,
        "evidence_status": evidence_status,
    }
    
def generate_expert_guide_answer(
    question: str,
    expert: str,
    country: str,
):
    import time
    from app.rag import client, MODEL_NAME
    from google.genai import types

    evidence = search_transcripts(
        query=question,
        n_results=5,
        country=country,
    )

    prompt = build_expert_guide_prompt(
        question=question,
        expert=expert,
        country=country,
        evidence=evidence,
    )

    max_attempts = 3

    for attempt in range(max_attempts):
        try:
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.1,
                ),
            )

            return {
                "question": question,
                "expert": expert,
                "country": country,
                "answer": response.text,
                "evidence": evidence,
            }

        except Exception as error:
            if "503" in str(error) or "UNAVAILABLE" in str(error):
                if attempt < max_attempts - 1:
                    time.sleep(3)
                    continue

            raise error
    
@app.get("/interview-guide")
def interview_guide():
    results = [
        {
            "question_id": question_item["id"],
            "question": question_item["question"],
        }
        for question_item in INTERVIEW_GUIDE
    ]

    return {
        "total_questions": len(INTERVIEW_GUIDE),
        "results": results,
    }


def select_guide_evidence(
    question_id: int,
    question: str,
) -> list[dict]:
    """Select one question-relevant expert passage per country."""

    terms = GUIDE_RELEVANCE_TERMS.get(question_id, ())
    selected = []

    for country in ("France", "Germany", "United Kingdom"):
        candidates = search_transcripts(
            query=question,
            n_results=10,
            country=country,
        )

        ranked = sorted(
            candidates,
            key=lambda item: (
                sum(
                    1
                    for term in terms
                    if term in item.get("text", "").lower()
                ),
                -item.get("distance", float("inf")),
            ),
            reverse=True,
        )

        if ranked:
            selected.append(ranked[0])

    return selected


@app.get("/interview-guide/{question_id}")
def interview_guide_question(question_id: int):
    question_item = next(
        (
            item
            for item in INTERVIEW_GUIDE
            if item["id"] == question_id
        ),
        None,
    )

    if question_item is None:
        return {
            "error": f"No interview guide question found for {question_id}"
        }

    question = question_item["question"]
    evidence = select_guide_evidence(question_id, question)

    if not evidence:
        return {
            "question_id": question_id,
            "question": question,
            "answer": "Insufficient evidence in the provided transcripts.",
            "evidence": [],
            "evidence_status": "Insufficient evidence",
        }

    generated = generate_grounded_answer(
        question=question,
        evidence=evidence,
    )

    return {
        "question_id": question_id,
        "question": question,
        "answer": generated["answer"],
        "evidence": evidence,
        "evidence_status": "Supported",
    }


def collect_insight_evidence() -> list[dict]:
    candidates = []

    for query in INSIGHTS_RETRIEVAL_QUERIES:
        for country in ("France", "Germany", "United Kingdom"):
            country_results = search_transcripts(
                query=query,
                n_results=6,
                country=country,
            )

            if country_results:
                candidates.append(country_results[0])

    selected = []
    seen = set()

    for item in candidates:
        key = (
            item.get("source"),
            item.get("timestamp"),
            item.get("text"),
        )

        if key in seen:
            continue

        seen.add(key)
        selected.append(item)

    return selected


@app.get("/insights")
def insights():
    evidence = collect_insight_evidence()
    print("INSIGHTS EVIDENCE:", evidence)

    if not evidence:
        return {
            "status": "insufficient",
            "themes": [],
            "differences": [],
            "outlook": "Insufficient evidence in the provided transcripts.",
            "evidence": [],
        }

    generated = generate_insights(evidence)

    return {
        "status": "supported",
        "themes": generated["themes"],
        "differences": generated["differences"],
        "outlook": generated["outlook"],
        "evidence": evidence,
    }