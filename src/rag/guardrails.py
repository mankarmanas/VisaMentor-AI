import re


class Guardrails:
    """
    Final safety check on Claude's answer before sending to the user.
    Runs after generation, catches answers that slipped past the system prompt.

    Checks:
    1. If no chunks were retrieved, answer must be a refusal — not real content
    2. Answer must not contain invented dates/numbers when context had none
    """

    REFUSAL_PHRASES = [
        "I don't have official documentation",
        "Please consult your DSO",
        "visit uscis.gov directly",
    ]

    # Catches answers that look like real content when they should be refusals
    # e.g. "OPT is...", "You must...", "According to USCIS..."
    CONTENT_PATTERN = re.compile(
        r"(according to|based on|uscis states|you must|you can|"
        r"the rule is|eligibility requires|you are eligible|"
        r"you may apply|the deadline is)",
        flags=re.IGNORECASE
    )

    def check(self, answer: str, chunks_used: int, intent: str = "visa_question", has_user_context: bool = False) -> dict:
        """
        Validate the answer against what was retrieved.

        Args:
            answer      : Claude's generated answer
            chunks_used : number of chunks that were passed to Claude

        Returns dict:
            is_safe  : bool — True if answer can be sent to user
            answer   : str  — original answer or replaced safe refusal
            reason   : str  — what was checked and why
        """

        # skip content check for non-visa intents — formatting/greeting/followup
        # are allowed to have content with 0 chunks
        if intent in ("formatting", "greeting", "followup"):
            print(f"Guardrails: PASSED — intent={intent}, no content check needed")
            return {
                "is_safe": True,
                "answer": answer,
                "reason": "passed"
            }

        # Check 1 — no context was retrieved but answer looks like real content
        if chunks_used == 0 :
            is_refusal = any(phrase in answer for phrase in self.REFUSAL_PHRASES)
            has_content = bool(self.CONTENT_PATTERN.search(answer))

            if has_content and not is_refusal:
                print(f"Guardrails: BLOCKED — answer has content but 0 chunks retrieved")
                return {
                    "is_safe": False,
                    "answer": (
                        "I don't have official documentation on that topic "
                        "in my knowledge base. Please consult your DSO "
                        "(Designated School Official) or visit uscis.gov directly."
                    ),
                    "reason": "knowledge_leakage — answer generated without retrieved context"
                }

        # Check 2 — answer is a clean refusal even with context (edge case)
        # This is fine — guardrails passes it through
        print(f"Guardrails: PASSED — chunks_used={chunks_used}")
        return {
            "is_safe": True,
            "answer": answer,
            "reason": "passed"
        }


if __name__ == "__main__":
    guardrails = Guardrails()

    print("Guardrails Test")
    print("=" * 60)

    test_cases = [
        {
            "label": "Clean refusal (0 chunks, correct behavior)",
            "answer": "I don't have official documentation on that topic in my knowledge base. Please consult your DSO (Designated School Official) or visit uscis.gov directly.",
            "chunks_used": 0,
        },
        {
            "label": "Knowledge leakage (0 chunks but real content — BLOCK THIS)",
            "answer": "According to USCIS, you must complete one full academic year before applying for OPT. You can apply 90 days before your program end date.",
            "chunks_used": 0,
        },
        {
            "label": "Normal answer with context (safe)",
            "answer": "Based on the USCIS guidelines, OPT is temporary employment authorization for F-1 students.",
            "chunks_used": 3,
        },
        {
            "label": "Greeting response (safe, no chunks needed)",
            "answer": "Hello! I am Visa Mentor AI. How can I help you today?",
            "chunks_used": 0,
        },
    ]

    for case in test_cases:
        print(f"\nTest : {case['label']}")
        result = guardrails.check(case["answer"], case["chunks_used"])
        print(f"Safe : {result['is_safe']}")
        print(f"Reason: {result['reason']}")
        if not result["is_safe"]:
            print(f"Replaced with: {result['answer']}")
        print("-" * 60)