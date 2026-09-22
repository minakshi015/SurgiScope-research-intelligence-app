from sentence_transformers import SentenceTransformer

# Local embedding model
# Produces 384-dimensional embeddings.
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

model = SentenceTransformer(MODEL_NAME)


def create_document_embeddings(texts: list[str]) -> list[list[float]]:
    """
    Create embeddings for transcript documents locally.
    No external embedding API is required.
    """
    embeddings = model.encode(
        texts,
        normalize_embeddings=True,
    )

    return embeddings.tolist()


def create_query_embedding(query: str) -> list[float]:
    """
    Create an embedding for a user query locally.
    Uses the same model as document embeddings.
    """
    embedding = model.encode(
        query,
        normalize_embeddings=True,
    )

    return embedding.tolist()