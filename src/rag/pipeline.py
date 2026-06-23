import os
from dotenv import load_dotenv
from src.rag.retriever import Retriever
from src.rag.generator import Generator
from src.rag.query_rewriter import QueryRewriter
from src.rag.guardrails import Guardrails
from src.rag.reranker import Reranker

load_dotenv()


class Pipeline:
    """
    Orchestrates the full RAG flow:
    user question → retrieve chunks → generate answer → return response
    Maintains chat history for multi-turn conversations.
    """

    MAX_HISTORY = 10  # keep last 10 messages to avoid token limit

    def __init__(self):
        self.retriever = Retriever()
        self.generator = Generator()
        self.rewriter = QueryRewriter()
        self.guardrails = Guardrails()
        self.reranker = Reranker()
        self.chat_history = []  # in-memory for MVP, PostgreSQL in Layer 3

    def _update_history(self, role: str, content: str):
        """Add message to chat history, trim if too long."""
        self.chat_history.append({
            "role": role,
            "content": content
        })
        # keep only last MAX_HISTORY messages
        if len(self.chat_history) > self.MAX_HISTORY:
            self.chat_history = self.chat_history[-self.MAX_HISTORY:]

    def _build_messages_with_history(self, question: str, chunks: list[dict]) -> list[dict]:
        """
        Build full messages list with:
        - previous chat history
        - current question with retrieved context
        """
        context = self.generator._build_context(chunks)

        current_message = (
            f"CONTEXT:\n{context}\n\n"
            f"QUESTION:\n{question}"
        )

        messages = []

        # add previous conversation history
        for msg in self.chat_history:
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })

        # add current question with context
        messages.append({
            "role": "user",
            "content": current_message
        })

        return messages


    def chat(self, question: str) -> dict:
        """
        Main method — takes user question, returns answer with metadata.
        """
        # Step 1 — classify intent and clean query
        rewrite = self.rewriter.classify(question)

        # Step 2 — retrieve only if needed
        if rewrite["needs_retrieval"]:
            query = rewrite["cleaned_query"] or question
            chunks = self.retriever.retrieve(query)
            chunks = self.reranker.rerank(query, chunks) 
        else:
            chunks = []
            print(f"Skipping retrieval — intent: {rewrite['intent']}")

        # Step 3 — build messages with history
        messages = self._build_messages_with_history(question, chunks)

        # Step 4 — generate answer
        response = self.generator.client.messages.create(
            model=self.generator.MODEL,
            max_tokens=self.generator.MAX_TOKENS,
            system=self.generator.SYSTEM_PROMPT,
            messages=messages
        )

        answer = response.content[0].text

        # Step 4.5 — safety check before sending to user
        guard = self.guardrails.check(answer, len(chunks), rewrite["intent"])
        answer = guard["answer"]

        # Step 5 — store plain question in history
        self._update_history("user", question)
        self._update_history("assistant", answer)

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

    def clear_history(self):
        """Clear chat history — called when user starts new conversation."""
        self.chat_history = []
        print("Chat history cleared.")


if __name__ == "__main__":
    pipeline = Pipeline()

    print("Visa Mentor AI - Test Chat")
    print("Type 'quit' to exit, 'clear' to clear history")
    print("=" * 50)

    while True:
        question = input("\nYou: ").strip()

        if question.lower() == "quit":
            break
        elif question.lower() == "clear":
            pipeline.clear_history()
            continue
        elif not question:
            continue

        result = pipeline.chat(question)

        print(f"\nAssistant: {result['answer']}")
        print(f"\n[Sources: {', '.join(set(s['source'] for s in result['sources']))}]")
        print(f"[Chunks used: {result['chunks_used']}]")