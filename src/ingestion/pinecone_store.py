import os
from pinecone import Pinecone
from dotenv import load_dotenv

load_dotenv()

class PineconeStore:
    """
    Handles upserting embedded chunks into Pinecone vector database.
    Uses upsert so re-running never creates duplicates.
    """

    BATCH_SIZE = 50

    def __init__(self):
        self.pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
        self.index = self.pc.Index(os.getenv("PINECONE_INDEX_NAME"))

    def _build_vector(self, chunk: dict, idx: int) -> dict:
        """Build a single Pinecone vector record from a chunk."""
        source = chunk["metadata"]["source"].lower()
        category = chunk["metadata"]["category"].lower()
        chunk_index = chunk["metadata"]["chunk_index"]

        vector_id = f"{source}_{category}_chunk_{chunk_index}_{idx}"

        return {
            "id": vector_id,
            "values": chunk["embedding"],
            "sparse_values": chunk["sparse_embedding"],
            "metadata": {
                "text": chunk["text"],
                "url": chunk["metadata"]["url"],
                "source": chunk["metadata"]["source"],
                "category": chunk["metadata"]["category"],
                "title": chunk["metadata"]["title"],
                "chunk_index": chunk["metadata"]["chunk_index"],
                "total_chunks": chunk["metadata"]["total_chunks"],
                "scraped_at": chunk["metadata"]["scraped_at"],
            }
        }

    def upsert_chunks(self, embedded_chunks: list[dict]):
        """
        Upsert all embedded chunks into Pinecone in batches.
        Upsert = insert if new, update if exists. No duplicates.
        """
        print(f"Upserting {len(embedded_chunks)} vectors to Pinecone...")

        vectors = [
            self._build_vector(chunk, idx)
            for idx, chunk in enumerate(embedded_chunks)
        ]

        for i in range(0, len(vectors), self.BATCH_SIZE):
            batch = vectors[i : i + self.BATCH_SIZE]
            self.index.upsert(vectors=batch)
            print(f" Upserted batch {i // self.BATCH_SIZE + 1} / {(len(vectors) - 1) // self.BATCH_SIZE + 1}")

        print(f"\n Done! {len(vectors)} vectors stored in Pinecone.")

    def get_stats(self):
        """Check how many vectors are in the index."""
        stats = self.index.describe_index_stats()
        print(f"Pinecone index stats: {stats}")
        return stats