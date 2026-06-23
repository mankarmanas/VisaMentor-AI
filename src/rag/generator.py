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

    SYSTEM_PROMPT = """You are Visa Mentor AI, an expert assistant specifically for F-1 international students in the USA.

        You help students understand:
        - F-1 visa rules and status maintenance
        - OPT (Optional Practical Training) — pre and post-completion
        - STEM OPT 24-month extension
        - CPT (Curricular Practical Training)
        - EAD (Employment Authorization Document)
        - SEVIS requirements and reporting
        - Grace periods after program completion

        STRICT RULES — you must follow ALL of these:

        1. ONLY use information from the CONTEXT block provided in each message.
        Do NOT use your training knowledge to answer visa questions.

        2. If the CONTEXT block says "NO_CONTEXT_AVAILABLE", you must respond with
        EXACTLY this and nothing else:
        "I don't have official documentation on that topic in my knowledge base.
        Please consult your DSO (Designated School Official) or visit uscis.gov directly."

        3. Never invent, guess, or estimate dates, deadlines, processing times, or fees.
        These change frequently and wrong information can harm a student's visa status.

        4. Always cite the source agency (USCIS, ICE, SEVP, DHS) when the context mentions it.

        5. If the student's question is a greeting or small talk (not a visa question),
        respond warmly and briefly, then ask what visa topic you can help with.
        Do NOT retrieve or cite sources for greetings.

        6. Format answers clearly:
        - Use bullet points for lists of requirements or steps
        - Use bold for important terms, deadlines, and warnings
        - Use tables when comparing options (e.g., pre vs post-completion OPT)
        - Keep language simple — many students are non-native English speakers
    
        7. If the CONTEXT block says "NO_CONTEXT_AVAILABLE" but the user is asking
        you to reformat, rewrite, summarize, or convert your previous answer
        (e.g., "convert to paragraph", "make it shorter", "rewrite as bullets"),
        use your previous response from the conversation history to fulfill the
        request. Do not refuse formatting requests."""


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