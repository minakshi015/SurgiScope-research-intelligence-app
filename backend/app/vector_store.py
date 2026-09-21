from pathlib import Path

import chromadb

from app.embeddings import (
    create_document_embeddings,
    create_query_embedding,
)


# ---------------------------------------------------------
# Project paths
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

CHROMA_DIR = PROJECT_ROOT / "chroma_db"


# ---------------------------------------------------------
# ChromaDB setup
# ---------------------------------------------------------

client = chromadb.PersistentClient(
    path=str(CHROMA_DIR)
)

collection = client.get_or_create_collection(
    name="expert_transcripts"
)


# ---------------------------------------------------------
# Index transcripts
# ---------------------------------------------------------

def index_transcripts(transcripts: list[dict]) -> int:
    """
    Convert transcript segments into embeddings
    and store them in ChromaDB with source metadata.
    """

    documents = []
    metadatas = []
    ids = []

    for transcript in transcripts:

        for index, segment in enumerate(
            transcript["segments"]
        ):

            documents.append(
                segment["text"]
            )

            metadatas.append(
                {
                    "expert": segment["expert"],
                    "country": segment["country"],
                    "timestamp": segment["timestamp"],
                    "speaker": segment["speaker"],
                    "source": segment["source"],
                }
            )

            ids.append(
                f"{segment['source']}_{index}"
            )

    if not documents:
        return 0

    embeddings = create_document_embeddings(
        documents
    )

    collection.upsert(
        ids=ids,
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas,
    )

    return len(documents)


# ---------------------------------------------------------
# Search transcript evidence
# ---------------------------------------------------------

def search_transcripts(
    query: str,
    n_results: int = 5,
    country: str | None = None,
) -> list[dict]:
    """
    Retrieve relevant expert transcript evidence.

    Interviewer statements are removed so that the
    generated answer is based on expert responses only.
    """

    query_embedding = create_query_embedding(
        query
    )

    # Retrieve more candidates than we finally need.
    # This gives us room to remove interviewer segments.
    candidate_count = max(
        n_results * 3,
        10,
    )

    query_args = {
        "query_embeddings": [query_embedding],
        "n_results": candidate_count,
    }

    # Country filtering, when requested.
    if country:
        query_args["where"] = {
            "country": country
        }

    results = collection.query(
        **query_args
    )

    documents = results.get(
        "documents",
        [[]],
    )[0]

    metadatas = results.get(
        "metadatas",
        [[]],
    )[0]

    distances = results.get(
        "distances",
        [[]],
    )[0]

    matches = []

    for document, metadata, distance in zip(
        documents,
        metadatas,
        distances,
    ):

        speaker = (
            metadata.get("speaker")
            or ""
        )

        # -------------------------------------------------
        # Ignore interviewer questions.
        # -------------------------------------------------

        if speaker.strip().lower() == "interviewer":
            continue

        matches.append(
            {
                "text": document,
                "expert": metadata.get(
                    "expert"
                ),
                "country": metadata.get(
                    "country"
                ),
                "timestamp": metadata.get(
                    "timestamp"
                ),
                "speaker": speaker,
                "source": metadata.get(
                    "source"
                ),
                "distance": distance,
            }
        )

        # Stop after collecting the requested
        # number of expert evidence chunks.
        if len(matches) >= n_results:
            break

    return matches