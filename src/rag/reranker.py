import os
import cohere
from dotenv import load_dotenv

load_dotenv()


class Reranker:
    """
    Re-orders retrieved chunks by relevance using Cohere Rerank API.

    Why: Pinecone ranks chunks by cosine similarity (vector closeness).
    Cohere reranks by actual relevance to the question — more accurate.

    Input:  question + list of chunks (already retrieved from Pinecone)
    Output: same chunks, re-ordered by relevance score, top N kept
    """

    TOP_N = 3  # keep top 3 after reranking (was 5 from Pinecone)
    MODEL = "rerank-english-v3.0"

    def __init__(self):
        self.client = cohere.ClientV2(
            api_key=os.getenv("COHERE_API_KEY")
        )

    def rerank(self, question: str, chunks: list[dict]) -> list[dict]:
        """
        Rerank chunks by relevance to question.

        Args:
            question : the cleaned query from QueryRewriter
            chunks   : list of chunk dicts from Retriever

        Returns:
            reranked list of chunk dicts, top N only
        """
        if not chunks:
            return []

        # Cohere needs plain text documents — extract text from chunk dicts
        documents = [chunk["text"] for chunk in chunks]

        response = self.client.rerank(
            model=self.MODEL,
            query=question,
            documents=documents,
            top_n=self.TOP_N,
        )

        # response.results contains items with index + relevance_score
        # use index to map back to original chunk dicts
        reranked = []
        for item in response.results:
            chunk = chunks[item.index]
            chunk["rerank_score"] = round(item.relevance_score, 4)
            reranked.append(chunk)

        print(f"Reranker: {len(chunks)} chunks → top {len(reranked)} after reranking")
        for i, chunk in enumerate(reranked):
            print(f"  {i+1}. rerank_score={chunk['rerank_score']} | {chunk['source']} | {chunk['category']}")

        return reranked


if __name__ == "__main__":
    from src.rag.retriever import Retriever

    retriever = Retriever()
    reranker = Reranker()

    question = "what is the 90 day rule for OPT application?"
    chunks = retriever.retrieve(question)

    print(f"\nBefore reranking ({len(chunks)} chunks):")
    for i, chunk in enumerate(chunks):
        print(f"  {i+1}. score={chunk['score']:.3f} | {chunk['source']} | {chunk['category']}")

    print(f"\nAfter reranking:")
    reranked = reranker.rerank(question, chunks)

    print(f"\nTop chunk text preview:")
    if reranked:
        print(reranked[0]["text"][:300])

    print(f"\n{'='*60}")
    print(f"COMPARISON — Before vs After Reranking")
    print(f"{'='*60}")

    print(f"\nTOP 5 from Pinecone (cosine similarity order):")
    for i, chunk in enumerate(chunks):
        print(f"\n  Chunk {i+1} | score={chunk['score']:.3f} | {chunk['source']} | {chunk['category']}")
        print(f"  {chunk['text'][:200]}...")

    print(f"\nTOP 3 after Reranker (relevance order):")
    for i, chunk in enumerate(reranked):
        print(f"\n  Chunk {i+1} | rerank_score={chunk['rerank_score']} | {chunk['source']} | {chunk['category']}")
        print(f"  {chunk['text'][:200]}...")