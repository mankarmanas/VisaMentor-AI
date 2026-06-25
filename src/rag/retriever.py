import os
from pinecone import Pinecone
from openai import OpenAI
from dotenv import load_dotenv
import re
from pinecone_text.sparse import BM25Encoder

load_dotenv()

BM25_PATH = "data/bm25_encoder.json"

class Retriever:
    """
    Queries Pinecone with user question and returns
    most relevant chunks for the LLM to answer from.
    """

    TOP_K = 5
    MIN_SCORE = 0.7

    FILLER_PATTERN = re.compile(
        r"^(hi+|hello|hey|hii+|helo|greetings|good\s+\w+)[,!.\s]*",
        flags=re.IGNORECASE
    )

    def __init__(self):
        self.pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
        self.index = self.pc.Index(os.getenv("PINECONE_INDEX_NAME"))
        self.openai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.bm25 = BM25Encoder()
        self.bm25 = self.bm25.load(BM25_PATH)

    def _clean_query(self, question: str) -> str:
        cleaned = self.FILLER_PATTERN.sub("", question).strip()
        return cleaned if cleaned else question

    def embed_query(self, question: str) -> list[float]:
        """Convert user question into a vector."""
        response = self.openai.embeddings.create(
            model="text-embedding-3-large",
            input=question,
        )
        return response.data[0].embedding

    def retrieve(self, question: str, filter: dict = None) -> list[dict]:
        """
        Embed the question, search Pinecone, return top chunks.
        Optional filter: {"category": "OPT"} or {"source": "USCIS"}
        """

        cleaned = self._clean_query(question)
        print(f"\nSearching for: '{cleaned}' (original: '{question}')")
        dense_vector = self.embed_query(cleaned)
        sparse_vector = self.bm25.encode_queries(cleaned)

        search_params = {
            "vector": dense_vector,
            "sparse_vector": sparse_vector,
            "top_k": self.TOP_K,
            "include_metadata": True,
        }

        if filter:
            search_params["filter"] = filter

        results = self.index.query(**search_params)

        print(f"Raw scores from Pinecone:")
        for match in results.matches:
            status = "PASS" if match.score >= self.MIN_SCORE else "FILTERED"
            print(f"  {status} | score={match.score:.3f} | {match.metadata.get('source', '')} | {match.metadata.get('category', '')}")

        chunks = []
        for match in results.matches:
            if match.score >= self.MIN_SCORE:
                chunks.append({
                    "text": match.metadata.get("text", ""),
                    "score": match.score,
                    "source": match.metadata.get("source", ""),
                    "category": match.metadata.get("category", ""),
                    "url": match.metadata.get("url", ""),
                    "title": match.metadata.get("title", ""),
                })

        print(f"Found {len(chunks)} relevant chunks (score >= {self.MIN_SCORE})")
        return chunks


if __name__ == "__main__":
    retriever = Retriever()

    question = "How do I apply for OPT?"
    chunks = retriever.retrieve(question)

    print(f"\n--- Top {len(chunks)} chunks ---")
    for i, chunk in enumerate(chunks):
        print(f"\nChunk {i+1} | Score: {chunk['score']:.3f} | Source: {chunk['source']} | Category: {chunk['category']}")
        print(f"Text: {chunk['text'][:200]}...")