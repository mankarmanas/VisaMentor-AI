import os
import json
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()


class QueryRewriter:
    """
    Classifies user message intent and cleans the query
    before it reaches the retriever.

    Intent types:
    - visa_question  → retrieve from Pinecone, answer with context
    - formatting     → reformat previous answer, no retrieval needed
    - greeting       → respond warmly, no retrieval needed
    - followup       → question about previous answer, no retrieval needed
    - out_of_scope   → not an F1 visa topic, refuse cleanly
    """

    MODEL = "claude-haiku-4-5-20251001"  # fast + cheap for classification

    CLASSIFIER_PROMPT = """You are a message classifier for a visa assistant chatbot.
    Classify the user message into exactly one of these intents:

    - visa_question  : asking about F1 visa, OPT, CPT, STEM OPT, EAD, SEVIS, grace period, I-20, I-765, Form I-20
    - formatting     : asking to reformat/rewrite/summarize the previous answer
    - greeting       : hello, hi, thanks, ok, good morning, small talk
    - followup       : question about the previous answer without a new visa topic
    - out_of_scope   : nothing to do with F1 visa (weather, math, coding, etc.)

    Respond with ONLY valid JSON in this exact format:
    {
    "intent": "<one of the 5 intents above>",
    "cleaned_query": "<the question rephrased clearly for search, or null if not visa_question>",
    "needs_retrieval": <true or false>
    }

    Rules:
    - cleaned_query should remove greetings, typos, filler words
    - Keep cleaned_query concise — do not expand or add words not in the original question
    - cleaned_query is null for non visa_question intents
    - needs_retrieval is true ONLY for visa_question"""

    def __init__(self):
        self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    def classify(self, question: str) -> dict:
        """
        Classify the user message and return intent + cleaned query.

        Returns dict with:
            intent         : str  — one of 5 intent types
            cleaned_query  : str | None — cleaned query for Pinecone
            needs_retrieval: bool — whether to hit Pinecone

        Example inputs and outputs:

        "hii what is OPT?" →
            {intent: "visa_question", cleaned_query: "what is OPT", needs_retrieval: True}

        "convert this to paragraph" →
            {intent: "formatting", cleaned_query: None, needs_retrieval: False}

        "hello!" →
            {intent: "greeting", cleaned_query: None, needs_retrieval: False}

        "what is the weather today?" →
            {intent: "out_of_scope", cleaned_query: None, needs_retrieval: False}

        "can you explain that again?" →
            {intent: "followup", cleaned_query: None, needs_retrieval: False}
        """
        response = self.client.messages.create(
            model=self.MODEL,
            max_tokens=300,
            system=self.CLASSIFIER_PROMPT,
            messages=[
                {"role": "user", "content": question}
            ]
        )

        raw = response.content[0].text.strip()

        # strip markdown code fences if Claude wraps the JSON
        if raw.startswith("```"):
            raw = raw.split("```")[1]          # get content between first ``` pair
            if raw.startswith("json"):
                raw = raw[4:]                  # strip the word "json" after ```
            raw = raw.strip()

        try:
            result = json.loads(raw)
        except json.JSONDecodeError:
            # if Claude returns malformed JSON, default to visa_question
            # so we never accidentally drop a real user query
            print(f"QueryRewriter: JSON parse failed on: {raw}")
            result = {
                "intent": "visa_question",
                "cleaned_query": question,
                "needs_retrieval": True
            }

        print(f"QueryRewriter: '{question}' → intent={result['intent']} | needs_retrieval={result['needs_retrieval']}")
        return result


if __name__ == "__main__":
    rewriter = QueryRewriter()

    test_cases = [
        "hii what is OPT?",
        "convert this to paragraph",
        "hello!",
        "what is the weather today?",
        "can you explain that again?",
        "when can I apply for STEM OPT extension?",
        "what is CPT?",
        "thanks",
        "ok got it",
        "how do I maintain my F1 status?",
    ]

    print("QueryRewriter Test")
    print("=" * 60)

    for question in test_cases:
        result = rewriter.classify(question)
        print(f"Input    : {question}")
        print(f"Intent   : {result['intent']}")
        print(f"Cleaned  : {result['cleaned_query']}")
        print(f"Retrieve : {result['needs_retrieval']}")
        print("-" * 60)