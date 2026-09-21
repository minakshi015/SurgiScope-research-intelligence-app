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
2. Do not invent facts, numbers, quotes, experts, countries, or timestamps.
3. If the evidence does not sufficiently answer the question, say exactly:
   "Insufficient evidence in the provided transcripts."
4. Compare experts only when the provided evidence supports the comparison.
5. Preserve uncertainty expressed by the experts.
6. Do not treat one expert's opinion as a fact about the entire market.
7. Do not create or guess citations, quotes, timestamps, or source names.
8. Keep the answer concise and research-oriented.
9. Mention disagreements only when the evidence actually supports them.

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
- "[exact quote]" (timestamp)

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
        }},
        {{
            "evidence_index": 2,
            "summary": "one or two sentence summary of this expert's emphasis"
        }},
        {{
            "evidence_index": 3,
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
- Use exactly one differences item for each of France, Germany, and the
    United Kingdom. Select an evidence index belonging to that country. The
    evidence includes a country label only to help select the correct index;
    the application supplies the displayed expert and country metadata.
- The outlook must begin by describing the views of the interviewed experts,
    not an official market forecast. Attribute every numeric growth estimate to
    the relevant evidence index. Never combine the estimates into a single
    market-wide prediction. Do not include expert names, countries, timestamps,
    source names, or labels such as "Evidence 7" in generated text; the
    application supplies identity and metadata from the selected evidence.
- Do not put expert names, countries, timestamps, source names, or quotes in
    generated summaries. Those are added from metadata by the application.
- If the evidence is insufficient for a field, use an empty list or exactly:
    "Insufficient evidence in the provided transcripts."

Transcript evidence:
{evidence_text}
"""