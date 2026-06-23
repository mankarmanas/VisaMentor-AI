from src.ingestion.chunker import Chunker
from src.ingestion.embedder import Embedder
from src.ingestion.pinecone_store import PineconeStore


def run():
    print("=" * 20)
    print("VISA MENTOR AI — Ingestion Pipeline")
    print("=" * 20)

    # Step 1 — Chunk all scraped documents
    print("\n Step 1: Chunking scraped documents...")
    chunker = Chunker()
    chunks = chunker.chunk_all()

    if not chunks:
        print(" No chunks found. Run web_scraper.py first.")
        return

    # Step 2 — Embed all chunks
    print("\n Step 2: Embedding chunks with OpenAI...")
    embedder = Embedder()
    embedded_chunks = embedder.embed_chunks(chunks)

    # Step 3 — Store in Pinecone
    print("\n Step 3: Storing vectors in Pinecone...")
    store = PineconeStore()
    store.upsert_chunks(embedded_chunks)

    # Step 4 — Verify
    print("\n Step 4: Verifying index...")
    store.get_stats()

    print("\n" + "=" * 20)
    print(" Ingestion complete!")
    print("=" * 20)


if __name__ == "__main__":
    run()