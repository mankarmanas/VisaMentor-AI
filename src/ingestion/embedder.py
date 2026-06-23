import os
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv
from pinecone_text.sparse import BM25Encoder

load_dotenv()

BM25_PATH = "data/bm25_encoder.json"

class Embedder:
    """
    Converts text chunks into vector embeddings
    using OpenAI text-embedding-3-large model.
    """

    MODEL = "text-embedding-3-large"
    DIMENSIONS = 3072
    BATCH_SIZE = 50

    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.bm25 = BM25Encoder()

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Embed a batch of texts and return list of vectors."""
        response = self.client.embeddings.create(
            model=self.MODEL,
            input=texts,
        )
        return [item.embedding for item in response.data]

    def embed_chunks(self, chunks: list[dict]) -> list[dict]:
        all_texts = [chunk["text"] for chunk in chunks]

        print(f"Fitting BM25 encoder on {len(chunks)} chunks...")
        self.bm25.fit(all_texts)

        print(f"Generating BM25 sparse vectors...")
        sparse_embeddings = self.bm25.encode_documents(all_texts)

        print(f"Embedding {len(chunks)} chunks with OpenAI in batches of {self.BATCH_SIZE}...")
        dense_embeddings = []

        for i in range(0, len(chunks), self.BATCH_SIZE):
            batch_texts = all_texts[i: i + self.BATCH_SIZE]
            print(f"  Processing batch {i // self.BATCH_SIZE + 1} / {(len(chunks) - 1) // self.BATCH_SIZE + 1}...")
            dense_embeddings.extend(self.embed_batch(batch_texts))

        embedded_chunks = []
        for chunk, dense, sparse in zip(chunks, dense_embeddings, sparse_embeddings):
            embedded_chunks.append({
                **chunk,
                "embedding": dense,
                "sparse_embedding": sparse,  
            })

        Path(BM25_PATH).parent.mkdir(parents=True, exist_ok=True)
        self.bm25.dump(BM25_PATH)
        print(f"BM25 encoder saved to {BM25_PATH}")

        print(f"Embedded {len(embedded_chunks)} chunks successfully")
        return embedded_chunks


if __name__ == "__main__":
    from src.ingestion.chunker import Chunker

    chunker = Chunker()
    chunks = chunker.chunk_all()

    embedder = Embedder()
    embedded = embedder.embed_chunks(chunks)

    print(f"\n--- Preview ---")
    print(f"Total embedded: {len(embedded)}")
    print(f"Vector size: {len(embedded[0]['embedding'])}")
    print(f"Sample metadata: {embedded[0]['metadata']}")