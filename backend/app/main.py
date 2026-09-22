from fastapi import FastAPI
import json
import re
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

STRONG_SEMANTIC_DISTANCE = 0.78
MAX_REVIEW_DISTANCE = 1.60
ASK_CANDIDATE_COUNT = 30

RELEVANCE_STOPWORDS = {
    "about", "after", "also", "and", "are", "been", "being", "does", "for",
    "from", "how", "into", "more", "most", "what", "when", "where", "which",
    "with", "would", "the", "their", "there", "this", "that", "than", "they",
    "them", "these", "those", "over", "under", "will", "were", "was", "have",
    "has", "had", "can", "could", "should", "did", "not", "in", "of", "to",
    "on", "by", "as", "at", "or", "an", "a", "is", "it", "its", "be", "do",
    "next", "current", "role", "robotic", "surgery", "europe", "market",
    "expert", "experts", "agree", "agreement",
}

RELEVANCE_CANONICAL_TERMS = {
    "adopt": "adoption",
    "adopting": "adoption",
    "adopted": "adoption",
    "growing": "growth",
    "grow": "growth",
    "increase": "growth",
    "increasing": "growth",
    "trend": "growth",
    "expected": "expect",
    "expectation": "expect",
    "purchasing": "purchase",
    "procurement": "purchase",
    "budgets": "budget",
    "hospitals": "hospital",
    "months": "month",
    "years": "year",
    "economics": "economic",
    "costs": "cost",
    "financial": "finance",
    "utilization": "utilisation",
    "centers": "centre",
    "centres": "centre",
    "outcomes": "outcome",
    "surgeons": "surgeon",
    "barriers": "barrier",
    "budgets": "budget",
    "investments": "investment",
    "returns": "return",
    "months": "month",
    "years": "year",
}

QUESTION_TOPICS = {
    "adoption": (
        "adoption", "access", "standard", "hospital", "centre", "university",
        "academic", "private", "regional", "community", "trust",
    ),
    "barriers": (
        "barrier", "cost", "capital", "budget", "funding", "finance",
        "approval", "economic", "utilisation", "training", "maintenance",
        "volume", "business case", "sustainable",
    ),
    "roi_economics": (
        "roi", "return", "investment", "economic", "cost", "budget", "capital",
        "finance", "utilisation", "procedure volume", "maintenance", "payback",
        "business case", "clinical strategy", "length of stay",
    ),
    "training_outcomes": (
        "training", "trained", "surgeon", "staff", "theatre", "clinical",
        "outcome", "length of stay", "recruitment", "utilisation", "procedure",
    ),
    "growth_outlook": (
        "trend", "growth", "growing", "increase", "increasing", "accelerate",
        "outlook", "expected", "expect", "future", "annual", "year",
    ),
    "purchasing_timeline": (
        "purchase", "procurement", "timeline", "time", "month", "approval",
        "committee", "capital cycle", "budget cycle", "funding", "buy",
    ),
}

TOPIC_PRIORITY = (
    "barriers",
    "roi_economics",
    "training_outcomes",
    "growth_outlook",
    "purchasing_timeline",
    "adoption",
)

TOPIC_STRONG_ANCHORS = {
    "adoption": (
        "adoption", "access", "standard", "uneven", "concentrated", "selected",
    ),
    "barriers": (
        "barrier", "capital budget approval", "economic case", "cost", "funding",
        "training capacity",
    ),
    "roi_economics": (
        "roi", "payback", "economic case", "economic", "finance", "total cost",
        "maintenance", "procedure volume", "clinical strategy", "length of stay",
    ),
    "training_outcomes": (
        "training", "trained", "surgeon", "staff", "theatre", "clinical",
        "outcome", "length of stay", "recruitment", "utilisation",
    ),
    "growth_outlook": (
        "expect", "expected", "outlook", "growth", "annual", "accelerate",
        "increase", "gradual", "future", "percent",
    ),
    "purchasing_timeline": (
        "month", "purchase", "procurement", "capital cycle", "budget cycle",
    ),
}

MIN_TOPIC_ANCHORS = {
    "growth_outlook": 2,
    "purchasing_timeline": 2,
}

BARRIER_DIRECT_ANCHORS = (
    "barrier", "capital budget approval", "funding", "training capacity",
)

UNSUPPORTED_QUERY_TERMS = (
    "market share", "revenue", "population", "sales", "market size",
    "company value", "profit", "2025 market",
)


def _relevance_terms(value: str) -> set[str]:
    """Return simple content terms for deterministic local relevance scoring."""

    terms = re.findall(r"[a-z0-9]+", value.lower())
    return {
        RELEVANCE_CANONICAL_TERMS.get(term, term)
        for term in terms
        if len(term) >= 3 and term not in RELEVANCE_STOPWORDS
    }


def _normalise_text(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()


def detect_question_topic(query: str) -> str | None:
    """Choose the most specific research intent using normalized anchor terms."""

    normalized_query = _normalise_text(query)
    query_terms = _relevance_terms(query)
    scores = {}

    for topic, anchors in QUESTION_TOPICS.items():
        score = 0
        for anchor in anchors:
            normalized_anchor = _normalise_text(anchor)
            if " " in normalized_anchor:
                score += 2 if normalized_anchor in normalized_query else 0
            elif normalized_anchor in query_terms:
                score += 1
        scores[topic] = score

    best_topic = max(
        TOPIC_PRIORITY,
        key=lambda topic: (scores[topic], -TOPIC_PRIORITY.index(topic)),
    )

    return best_topic if scores[best_topic] else None


def _contains_anchor(text: str, anchor: str) -> bool:
    normalized_text = _normalise_text(text)
    normalized_anchor = _normalise_text(anchor)

    if " " in normalized_anchor:
        return normalized_anchor in normalized_text

    return normalized_anchor in _relevance_terms(text)


def _topic_anchor_score(topic: str, text: str) -> int:
    return sum(
        1
        for anchor in TOPIC_STRONG_ANCHORS[topic]
        if _contains_anchor(text, anchor)
    )


def _is_relevant_evidence(
    query: str,
    item: dict,
    topic: str | None = None,
) -> bool:
    """Require semantic, question-term, and topic-specific evidence signals."""

    query_terms = _relevance_terms(query)
    text = item.get("text", "")
    text_terms = _relevance_terms(text)
    overlap = query_terms & text_terms
    distance = item.get("distance", float("inf"))
    topic = topic or detect_question_topic(query)

    if (
        not query_terms
        or not topic
        or not isinstance(distance, (int, float))
    ):
        return False

    topic_score = _topic_anchor_score(topic, text)
    if topic == "barriers" and not any(
        _contains_anchor(text, anchor)
        for anchor in BARRIER_DIRECT_ANCHORS
    ):
        return False

    if (
        topic_score < MIN_TOPIC_ANCHORS.get(topic, 1)
        or distance > MAX_REVIEW_DISTANCE
    ):
        return False

    overlap_ratio = len(overlap) / len(query_terms)

    # Two direct topic anchors can establish relevance even when the expert
    # uses different wording from the question (for example, "total cost of
    # ownership" for an ROI question).
    if topic_score >= 2 and distance <= MAX_REVIEW_DISTANCE:
        return True

    # Strong semantic retrieval still needs a topic-specific anchor. This
    # prevents a generic adoption passage from supporting a barriers question.
    if distance <= STRONG_SEMANTIC_DISTANCE and overlap and topic_score >= 1:
        return True

    return (
        topic_score >= 1
        and len(overlap) >= 1
        and overlap_ratio >= 0.20
    )


def _evidence_score(query: str, item: dict, topic: str) -> tuple:
    query_terms = _relevance_terms(query)
    text_terms = _relevance_terms(item.get("text", ""))
    overlap = query_terms & text_terms
    topic_score = _topic_anchor_score(topic, item.get("text", ""))
    distance = item.get("distance", float("inf"))

    if topic == "roi_economics":
        return (
            -distance,
            topic_score,
            len(overlap),
        )

    return (
        topic_score,
        -distance,
        len(overlap),
    )


def _select_balanced_evidence(
    query: str,
    candidates: list[dict],
    topic: str,
    limit: int,
) -> list[dict]:
    relevant = [
        item
        for item in candidates
        if _is_relevant_evidence(query, item, topic)
    ]
    ranked = sorted(
        relevant,
        key=lambda item: _evidence_score(query, item, topic),
        reverse=True,
    )

    selected = []
    selected_keys = set()

    # One strongest passage per expert gives cross-expert questions balanced
    # evidence before any additional passages are considered.
    for item in ranked:
        expert_key = item.get("expert") or item.get("country")
        if expert_key in selected_keys:
            continue
        selected.append(item)
        selected_keys.add(expert_key)
        if len(selected) >= limit:
            return selected

    for item in ranked:
        if item in selected:
            continue
        selected.append(item)
        if len(selected) >= limit:
            break

    return selected

GUIDE_RELEVANCE_TERMS = {
    1: (
        "adoption", "growing", "concentrated", "academic", "university",
        "private", "nhs", "hospital", "hospitals", "regional", "access",
        "uneven", "advanced", "waiting", "standard", "selected",
    ),
    2: (
        "barrier", "cost", "capital", "budget", "funding", "finance",
        "approval", "training capacity", "economic case",
    ),
    3: (
        "roi", "capital", "budget", "procedure", "volume", "utilisation",
        "utilization", "maintenance", "pay", "cost", "economic", "finance",
        "business case", "investment", "outcomes", "recruitment",
    ),
    4: (
        "training", "trained", "surgeon", "surgeons", "theatre", "staff",
        "outcomes", "clinical", "utilisation", "utilization", "procedure",
        "operational",
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
    normalized_query = _normalise_text(query)
    has_unsupported_request = any(
        term in normalized_query
        for term in UNSUPPORTED_QUERY_TERMS
    )
    topic = detect_question_topic(query)

    if has_unsupported_request or topic is None:
        evidence = []
    else:
        candidates = search_transcripts(
            query,
            max(n_results, ASK_CANDIDATE_COUNT),
        )
        evidence = _select_balanced_evidence(
            query=query,
            candidates=candidates,
            topic=topic,
            limit=n_results,
        )

    if evidence:
        generated = generate_grounded_answer(
            question=query,
            evidence=evidence,
        )
        answer = generated["answer"]
        perspective = generated["perspective"]
        expert_count = len({item.get("expert") for item in evidence})
        evidence_status = (
            "Supported"
            if expert_count >= 2
            else "Limited evidence"
        )
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