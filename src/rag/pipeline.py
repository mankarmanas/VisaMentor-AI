from dotenv import load_dotenv
from src.rag.retriever import Retriever
from src.rag.generator import Generator
from src.rag.query_rewriter import QueryRewriter
from src.rag.guardrails import Guardrails
from src.rag.reranker import Reranker

load_dotenv()


class Pipeline:

    def __init__(self):
        self.retriever = Retriever()
        self.generator = Generator()
        self.rewriter = QueryRewriter()
        self.guardrails = Guardrails()
        self.reranker = Reranker()

    def _build_messages_with_history(
        self, question: str, chunks: list[dict], history: list[dict]
    ) -> list[dict]:
        context = self.generator._build_context(chunks)

        current_message = (
            f"CONTEXT:\n{context}\n\n"
            f"QUESTION:\n{question}"
        )

        messages = []

        for msg in history:
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })

        messages.append({
            "role": "user",
            "content": current_message
        })

        return messages

    def chat(self, question: str, history: list[dict] = []) -> dict:
        # Step 1 — classify intent and clean query
        rewrite = self.rewriter.classify(question)

        # Step 2 — retrieve only if needed
        if rewrite["needs_retrieval"]:
            query = rewrite["cleaned_query"] or question
            chunks = self.retriever.retrieve(query)
            chunks = self.reranker.rerank(query, chunks)
        else:
            chunks = []

        # Step 3 — build messages with history from DB
        messages = self._build_messages_with_history(question, chunks, history)

        # Step 4 — generate answer
        response = self.generator.client.messages.create(
            model=self.generator.MODEL,
            max_tokens=self.generator.MAX_TOKENS,
            system=self.generator.SYSTEM_PROMPT,
            messages=messages
        )

        answer = response.content[0].text

        # Step 5 — guardrails check
        guard = self.guardrails.check(answer, len(chunks), rewrite["intent"])
        answer = guard["answer"]

        return {
            "question": question,
            "answer": answer,
            "intent": rewrite["intent"],
            "sources": [
                {
                    "source": c["source"],
                    "url": c["url"],
                    "category": c["category"],
                    "score": c["score"],
                }
                for c in chunks
            ],
            "chunks_used": len(chunks),
        }


if __name__ == "__main__":
    pipeline = Pipeline()

    print("Visa Mentor AI - Test Chat")
    print("Type 'quit' to exit")
    print("=" * 50)

    while True:
        question = input("\nYou: ").strip()

        if question.lower() == "quit":
            break
        elif not question:
            continue

        result = pipeline.chat(question)

        print(f"\nAssistant: {result['answer']}")
        print(f"\n[Sources: {', '.join(set(s['source'] for s in result['sources']))}]")
        print(f"[Chunks used: {result['chunks_used']}]")