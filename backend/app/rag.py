from google import genai
from google.genai import types
import os
import re
import json
from pathlib import Path
from dotenv import load_dotenv

from app.prompts import build_grounded_prompt, build_insights_prompt


PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")


MODEL_NAME = "gemini-3.5-flash-lite"

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def _extract_json(response_text: str) -> dict:
    cleaned = response_text.strip()

    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", cleaned)

    try:
        parsed = json.loads(cleaned)
        return parsed if isinstance(parsed, dict) else {}
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", cleaned, flags=re.DOTALL)

        if not match:
            return {}

        try:
            parsed = json.loads(match.group(0))
            return parsed if isinstance(parsed, dict) else {}
        except json.JSONDecodeError:
            return {}


def generate_grounded_answer(
    question: str,
    evidence: list[dict],
) -> dict:

    prompt = build_grounded_prompt(question, evidence)

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.1,
        ),
    )

    response_text = (response.text or "").strip()

    answer_match = re.search(
        r"(?:^|\n)\s*ANSWER\s*:\s*(.*?)(?=\n\s*PERSPECTIVE\s*:|$)",
        response_text,
        flags=re.IGNORECASE | re.DOTALL,
    )
    perspective_match = re.search(
        r"(?:^|\n)\s*PERSPECTIVE\s*:\s*(.*)$",
        response_text,
        flags=re.IGNORECASE | re.DOTALL,
    )

    perspectives = []

    if perspective_match:
        perspective_lines = perspective_match.group(1).strip().splitlines()

        for line in perspective_lines:
            line_match = re.match(
                r"\s*Evidence\s+(\d+)\s*:\s*(.+?)\s*$",
                line,
                flags=re.IGNORECASE,
            )

            if not line_match:
                continue

            evidence_index = int(line_match.group(1)) - 1

            if evidence_index < 0 or evidence_index >= len(evidence):
                continue

            source = evidence[evidence_index]

            if any(
                item["expert"] == source.get("expert")
                for item in perspectives
            ):
                continue

            perspectives.append(
                {
                    "expert": source.get("expert"),
                    "country": source.get("country"),
                    "summary": line_match.group(2).strip(),
                }
            )

    if not answer_match and not perspective_match:
        return {
            "answer": response_text,
            "perspective": [],
        }

    return {
        "answer": (
            answer_match.group(1).strip()
            if answer_match
            else response_text
        ),
        "perspective": perspectives,
    }


def generate_insights(evidence: list[dict]) -> dict:
    prompt = build_insights_prompt(evidence)

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.1,
            response_mime_type="application/json",
        ),
    )

    parsed = _extract_json(response.text or "")
    evidence_count = len(evidence)

    def valid_index(value):
        return isinstance(value, int) and 1 <= value <= evidence_count

    themes = []

    for theme in parsed.get("themes", []):
        if not isinstance(theme, dict):
            continue

        indices = [
            value
            for value in theme.get("evidence_indices", [])
            if valid_index(value)
        ]
        supporting = [evidence[value - 1] for value in indices]
        experts = list(dict.fromkeys(
            item.get("country")
            for item in supporting
            if item.get("country")
        ))

        if theme.get("title") and theme.get("summary") and supporting:
            themes.append({
                "title": str(theme["title"]).strip(),
                "summary": str(theme["summary"]).strip(),
                "experts": experts,
            })

    differences = []
    difference_experts = set()

    for difference in parsed.get("differences", []):
        if not isinstance(difference, dict):
            continue

        index = difference.get("evidence_index")

        if not valid_index(index) or not difference.get("summary"):
            continue

        source = evidence[index - 1]

        if source.get("expert") in difference_experts:
            continue

        difference_experts.add(source.get("expert"))
        differences.append({
            "expert": source.get("expert"),
            "country": source.get("country"),
            "summary": str(difference["summary"]).strip(),
        })

    outlook_data = parsed.get("outlook", {})
    outlook = {
        "summary": "",
        "points": [],
    }

    if isinstance(outlook_data, dict):
        outlook["summary"] = str(
            outlook_data.get("summary", "")
        ).strip()

        for point in outlook_data.get("points", []):
            if not isinstance(point, dict):
                continue

            index = point.get("evidence_index")

            if not valid_index(index) or not point.get("summary"):
                continue

            source = evidence[index - 1]
            outlook["points"].append({
                "expert": source.get("expert"),
                "country": source.get("country"),
                "summary": str(point["summary"]).strip(),
            })
    else:
        outlook["summary"] = str(outlook_data or "").strip()

    return {
        "themes": themes,
        "differences": differences,
        "outlook": outlook,
    }