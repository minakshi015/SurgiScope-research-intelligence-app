INTERVIEW_GUIDE = [
    {
        "id": 1,
        "question": "What is the current adoption of robotic surgery in Europe?"
    },
    {
        "id": 2,
        "question": "What are the main barriers to robotic surgery adoption?"
    },
    {
        "id": 3,
        "question": "How important are hospital budgets and ROI when adopting robotic surgery?"
    },
    {
        "id": 4,
        "question": "How important are surgeon training and clinical outcomes?"
    },
    {
        "id": 5,
        "question": "What is the expected adoption trend over the next 3–5 years?"
    },
    {
        "id": 6,
        "question": "What is the typical hospital purchasing timeline for robotic surgery?"
    },
]


def build_grounded_prompt(
    question: str,
    evidence: list[dict],
) -> str:

    evidence_text = ""

    for index, item in enumerate(evidence, start=1):
        evidence_text += f"""
Evidence {index}:
Expert: {item.get("expert")}
Country: {item.get("country")}
Timestamp: {item.get("timestamp")}
Source: {item.get("source")}
Transcript text: {item.get("text")}
"""

    return f"""
You are an AI research assistant analyzing expert interviews about
the European robotic surgery market.

Answer the user's question using ONLY the transcript evidence provided below.

IMPORTANT RULES:
1. Do not use outside knowledge.
2. Do not invent facts, numbers, quotes, experts, countries, timestamps,
   sources, or conclusions.
3. If the evidence does not sufficiently answer the question, say exactly:
   "Insufficient evidence in the provided transcripts."
4. Treat each expert's statement as that expert's perspective, not as a
   fact about the entire European market.
5. Do not generalize one expert's statement to all experts.
6. Only describe a consensus when multiple experts provide evidence
   supporting the same point.
7. If experts differ in emphasis, interpretation, estimates, or priorities,
   explicitly preserve that difference.
8. Do not hide meaningful disagreement by combining conflicting views into
   one general statement.
9. Preserve uncertainty, conditions, ranges, and qualifiers expressed by
   the experts.
10. Numeric estimates must remain attributed to the relevant expert evidence.
    Never combine different expert estimates into one market-wide number.
11. Compare experts only when the provided evidence directly supports
    the comparison.
12. Do not create or guess citations, quotes, timestamps, or source names.
13. Retrieval relevance is not proof by itself: make each factual claim only
    when the transcript text directly supports it.
14. For questions about agreement or disagreement, state the shared point
    first only when at least two experts support it, then preserve differences
    in emphasis, conditions, or estimates.
15. The supplied evidence has been deterministically filtered for the
    question topic. Do not use a passage merely because it is loosely related
    to robotic surgery; omit claims that the passage does not directly support.
16. Keep the answer concise, neutral, and research-oriented.

ANSWER WRITING RULES:
- First summarize the strongest point supported across the evidence.
- Then mention important differences or qualifications when present.
- Do not say "all experts agree" unless the evidence genuinely supports that.
- Prefer wording such as "the interviews suggest", "the experts
  consistently highlight", or "views differ on" when appropriate.
- When evidence is mixed, clearly distinguish the shared point from the
  differing expert perspectives.
- Never turn a possibility, expectation, or conditional statement into a
    definite prediction. Keep qualifiers such as "may", "could", "likely",
    "if", and "in some areas" when they affect meaning.
- Never combine expert-specific numeric ranges into a single market figure.

Return ONLY these two sections. Do not include key evidence, quotes,
timestamps, source names, or any other sections:

ANSWER:
[A concise 2-4 sentence synthesis based only on the evidence.]

PERSPECTIVE:
[Write one short statement for each distinct expert represented in the
evidence. Use the strongest relevant evidence for each expert. Use exactly
this format, where the number refers to the evidence number above:

Evidence 1: [one or two sentences describing only this expert's perspective]
Evidence 2: [one or two sentences describing only this expert's perspective]

Do not include expert names, countries, timestamps, citations, or quotes in
these lines. If a perspective is not supported, omit that expert's line.]

User question:
{question}

Transcript evidence:
{evidence_text}
"""


def build_expert_guide_prompt(
    question: str,
    expert: str,
    country: str,
    evidence: list[dict],
) -> str:
    evidence_text = ""

    for index, item in enumerate(evidence, start=1):
        evidence_text += f"""
Evidence {index}:
Expert: {item.get("expert")}
Country: {item.get("country")}
Timestamp: {item.get("timestamp")}
Source: {item.get("source")}
Transcript text: {item.get("text")}
"""

    return f"""
You are analyzing one expert interview for a research study on
the European robotic surgery market.

Expert:
{expert}

Country:
{country}

Interview question:
{question}

Answer the question using ONLY the transcript evidence provided below.

IMPORTANT RULES:
1. Do not use outside knowledge.
2. Do not invent facts, numbers, quotes, or timestamps.
3. Answer only from this expert's transcript.
4. If the evidence does not sufficiently answer the question, say:
   "Insufficient evidence in this transcript."
5. Preserve uncertainty expressed by the expert.
6. Do not generalize this expert's opinion to the entire European market.
7. Keep the answer concise and research-oriented.
8. Exact quotes must be copied from the provided transcript text.

Return:

Answer:
[concise answer based only on the evidence]

Key evidence:
-- "[exact quote]" (timestamp)

Evidence status:
[Supported / Limited evidence / Insufficient evidence]

Transcript evidence:
{evidence_text}
"""


def build_insights_prompt(evidence: list[dict]) -> str:
    evidence_text = ""

    for index, item in enumerate(evidence, start=1):
        evidence_text += f"""
Evidence {index}:
Country label for mapping only: {item.get("country")}
Transcript text: {item.get("text")}
"""

    return f"""
You are an AI research analyst synthesizing three expert interviews about
the European robotic surgery market.

Use ONLY the transcript evidence below. Do not use outside knowledge.
Do not invent facts, numbers, quotes, timestamps, experts, countries, or
sources. Preserve uncertainty and do not treat one expert's view as a
market-wide fact. A theme must be supported by more than one expert where
possible. Differences must reflect actual differences in the evidence.

Return ONLY valid JSON with this exact shape:
{{
    "themes": [
        {{
            "title": "short theme title",
            "summary": "one or two sentence synthesis",
            "evidence_indices": [1, 2]
        }}
    ],
    "differences": [
        {{
            "evidence_index": 1,
            "summary": "one or two sentence summary of this expert's emphasis"
        }}
    ],
    "outlook": {{
        "summary": "one sentence beginning with Across the interviewed experts",
        "points": [
            {{
                "evidence_index": 1,
                "summary": "one sentence describing this expert's outlook, including attributed numeric estimates when present"
            }}
        ]
    }}
}}

Rules for the JSON:
- Use evidence_indices only for evidence that directly supports the statement.
- Use one differences item for each represented country. Select an evidence
  index belonging to that country.
- Attribute every numeric growth estimate to its evidence index. Never combine
  estimates into a single market-wide prediction.
- Do not put expert names, countries, timestamps, source names, or quotes in
  generated summaries; the application supplies identity and metadata.
- If evidence is insufficient for a field, use an empty list or exactly:
  "Insufficient evidence in the provided transcripts."

Transcript evidence:
{evidence_text}
"""