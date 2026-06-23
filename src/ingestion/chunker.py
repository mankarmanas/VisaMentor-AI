import json
from pathlib import Path
from langchain_text_splitters import RecursiveCharacterTextSplitter


SCRAPED_DIR = Path("data/scraped")


class Chunker:
    """
    Reads scraped JSON files and splits content into
    smaller chunks with metadata preserved on every chunk.
    """

    def __init__(self, chunk_size: int = 800, chunk_overlap: int = 150):
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""],
        )

    def chunk_document(self, document: dict) -> list[dict]:
        """Split a single document into chunks with metadata."""
        chunks = self.splitter.split_text(document["content"])
        result = []

        for i, chunk_text in enumerate(chunks):
            result.append({
                "text": chunk_text,
                "metadata": {
                    "url": document["url"],
                    "source": document["source"],
                    "category": document["category"],
                    "title": document["title"],
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                    "scraped_at": document["scraped_at"],
                }
            })

        return result

    def chunk_all(self, scraped_dir: Path = SCRAPED_DIR) -> list[dict]:
        """Read all scraped JSON files and chunk them."""
        files = list(scraped_dir.glob("*.json"))

        if not files:
            print("No scraped files found.")
            return []

        print(f"Chunking {len(files)} scraped files...")

        all_chunks = []

        for filepath in files:
            with open(filepath, "r", encoding="utf-8") as f:
                document = json.load(f)

            chunks = self.chunk_document(document)
            all_chunks.extend(chunks)

            print(f" {document['title'][:50]} → {len(chunks)} chunks")

        print(f"\nTotal chunks: {len(all_chunks)}")
        return all_chunks


if __name__ == "__main__":
    chunker = Chunker()
    chunks = chunker.chunk_all()

    # Preview first chunk
    if chunks:
        print("\n--- Preview of first chunk ---")
        print(f"Text: {chunks[0]['text'][:200]}...")
        print(f"Metadata: {chunks[0]['metadata']}")