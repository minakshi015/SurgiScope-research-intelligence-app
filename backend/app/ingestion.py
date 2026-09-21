from pathlib import Path
import re


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"


def parse_transcript(file_path: Path) -> dict:
    """
    Read one transcript and extract:
    - expert
    - role
    - country
    - timestamped conversation segments
    """

    content = file_path.read_text(encoding="utf-8")

    # Basic transcript metadata
    expert_match = re.search(
        r"Expert\s+\d+\s+[–-]\s+(.+)",
        content
    )

    role_match = re.search(
        r"Role:\s*(.+)",
        content
    )

    market_match = re.search(
        r"Market:\s*(.+)",
        content
    )

    expert = expert_match.group(1).strip() if expert_match else "Unknown"
    role = role_match.group(1).strip() if role_match else "Unknown"
    country = market_match.group(1).strip() if market_match else "Unknown"

    # Find timestamped conversation segments
    pattern = re.compile(
        r"(?m)^(\d{2}:\d{2})\s*$\n"
        r"([A-Za-z .]+):\s*(.+)$"
    )

    segments = []

    for match in pattern.finditer(content):
        timestamp = match.group(1)
        speaker = match.group(2).strip()
        text = match.group(3).strip()

        segments.append({
            "timestamp": timestamp,
            "speaker": speaker,
            "text": text,
            "expert": expert,
            "country": country,
            "source": file_path.name,
        })

    return {
        "expert": expert,
        "role": role,
        "country": country,
        "source": file_path.name,
        "segments": segments,
    }


def load_all_transcripts() -> list[dict]:
    """
    Load all expert transcripts from the data folder.
    """

    transcript_files = sorted(
        DATA_DIR.glob("Transcript_*.txt")
    )

    transcripts = []

    for file_path in transcript_files:
        transcripts.append(
            parse_transcript(file_path)
        )

    return transcripts