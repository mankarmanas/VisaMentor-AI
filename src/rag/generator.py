import os
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()


class Generator:
    """
    Takes retrieved chunks and user question,
    sends to Claude Sonnet 4.6 and returns answer.
    """

    MODEL = "claude-sonnet-4-6"
    MAX_TOKENS = 2048

    SYSTEM_PROMPT = """You are Visa Mentor AI, an F-1 visa assistant. You operate in STRICT RAG MODE.

    ABSOLUTE RULES — violating any of these is a critical failure:

    1. CONTEXT IS YOUR ONLY SOURCE OF TRUTH.
    You have no knowledge. You are a relay for the documents in the CONTEXT block.
    Only state facts that appear in the CONTEXT. If a fact is not in the CONTEXT, do not say it.
    Do NOT write inline citations like [Source 1] or [Source 2] anywhere in your response.
    Sources are shown separately in the UI — never add them inline.

    2. IF CONTEXT IS INSUFFICIENT:
    Say exactly: "I don't have official documentation on [topic] in my knowledge base."
    Then suggest 1-2 related topics you DO have sources for.
    End with: "Your DSO at [university] can answer this directly."
    Do NOT attempt to help further using your own knowledge.

    3. NEVER extrapolate, infer, or extend beyond what the sources explicitly state.
    If the source says "students may work", do not add conditions the source didn't mention.
    Copy the meaning from the source — do not improve or complete it.

    4. NEVER invent processing times, fees, deadlines, or form numbers not in the CONTEXT.

    5. GREETINGS: respond warmly and briefly, ask what visa topic you can help with. No sources needed.

    6. FORMATTING:
    - Bullets for lists
    - Bold for deadlines and warnings
    - Simple language for non-native speakers

    7. FORMATTING REQUESTS (reformat/rewrite/convert):
    Use your previous response from conversation history. Do not retrieve new sources.

    8. STUDENT PROFILE data (dates, eligibility, deadlines) comes from the system — you may use
    it freely without [Source N] citation since it is calculated from official rules, not pretrained knowledge."""


    def __init__(self):
        self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    def _build_context(self, chunks: list[dict]) -> str:
        """Format retrieved chunks into context string for Claude.Returns NO_CONTEXT_AVAILABLE when chunks is empty so the
        system prompt rule #2 triggers a clean refusal."""

        if not chunks:
            return "NO_CONTEXT_AVAILABLE"

        context_parts = []
        for i, chunk in enumerate(chunks):
            context_parts.append(
                f"[Source {i+1}: {chunk['source']} | {chunk['category']}]\n"
                f"{chunk['text']}\n"
                f"Reference: {chunk['url']}"
            )

        return "\n\n---\n\n".join(context_parts)
    

    def generate(self, question: str, chunks: list[dict]) -> str:
        """Generate answer from question + retrieved chunks."""
        context = self._build_context(chunks)

        user_message = (
            f"CONTEXT:\n{context}\n\n"
            f"QUESTION:\n{question}"
        )

        response = self.client.messages.create(
            model=self.MODEL,
            max_tokens=self.MAX_TOKENS,
            system=self.SYSTEM_PROMPT,
            messages=[
                {"role": "user", "content": user_message}
            ]
        )

        return response.content[0].text


if __name__ == "__main__":
    from src.rag.retriever import Retriever

    question = "How do I apply for OPT?"

    retriever = Retriever()
    chunks = retriever.retrieve(question)

    generator = Generator()
    answer = generator.generate(question, chunks)

    print(f"\n{'='*50}")
    print(f"Question: {question}")
    print(f"{'='*50}")
    print(f"Answer:\n{answer}")
    print(f"{'='*50}")