from dotenv import load_dotenv
from src.rag.retriever import Retriever
from src.rag.generator import Generator
from src.rag.query_rewriter import QueryRewriter
from src.rag.guardrails import Guardrails
from src.rag.reranker import Reranker
from src.rag.date_engine import DateEngine
from src.db.database import get_db
from src.db.crud import UserCRUD
from datetime import date
import anthropic
import os
import re
import json

load_dotenv()

class Pipeline:

    HAIKU_MODEL = "claude-haiku-4-5-20251001"

    def __init__(self):
        self.retriever = Retriever()
        self.generator = Generator()
        self.rewriter = QueryRewriter()
        self.guardrails = Guardrails()
        self.reranker = Reranker()
        self.date_engine = DateEngine()
        self.haiku = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    def _extract_opt_date(self, question: str) -> str | None:
        prompt = f"""Does this message mention an OPT start date that the student has chosen or is planning to choose?

        If yes, return ONLY the date in YYYY-MM-DD format. Nothing else.
        If no, return NONE.

        Examples:
        "my OPT starts June 15 2026" → 2026-06-15
        "I chose July 1 as my OPT start date" → 2026-07-01
        "when does my OPT end?" → NONE
        "what is OPT?" → NONE

        Message: {question}"""

        response = self.haiku.messages.create(
            model=self.HAIKU_MODEL,
            max_tokens=20,
            messages=[{"role": "user", "content": prompt}]
        )

        result = response.content[0].text.strip()
        if result == "NONE":
            return None

        # validate it looks like a date
        if re.match(r"\d{4}-\d{2}-\d{2}", result):
            return result
        return None

    def _save_opt_start_date(self, uid: str, date_str: str):
        db = next(get_db())
        try:
            UserCRUD.update_opt_start_date(
                db=db,
                uid=uid,
                opt_start_date=date.fromisoformat(date_str),
            )
            print(f"OPT start date saved: {date_str}")
        except Exception as e:
            print(f"Failed to save OPT start date: {e}")
        finally:
            db.close()

    STEM_KEYWORDS = {
        "computer science", "computer engineering", "data science", "data analytics",
        "artificial intelligence", "machine learning", "information technology",
        "information systems", "software engineering", "electrical engineering",
        "mechanical engineering", "civil engineering", "chemical engineering",
        "mathematics", "statistics", "physics", "biology", "chemistry",
        "bioinformatics", "cybersecurity", "network engineering", "robotics",
    }

    def _is_likely_stem(self, program: str) -> bool:
        program_lower = program.lower()
        return any(keyword in program_lower for keyword in self.STEM_KEYWORDS)

    def _build_user_context(self, uid: str) -> str:
        if not uid:
            return ""

        db = next(get_db())
        try:
            user = UserCRUD.get_by_uid(db, uid)
            if not user or not user.university:
                return ""

            context_lines = [
                "STUDENT PROFILE:",
                f"  Name: {user.name}",
                f"  University: {user.university}",
                f"  Program: {user.program}",
                f"  STEM Eligible: {'Yes' if user.stem_eligible else 'No'}",
                *(
                    [
                        "  ⚠️ STEM MISMATCH WARNING: The student's program appears to be STEM-eligible "
                        f"('{user.program}' matches known STEM fields), but the student marked "
                        "stem_eligible=No during profile setup. This may be a mistake. "
                        "Inform the student that their degree likely qualifies for STEM OPT and "
                        "they should verify with their DSO and update their profile."
                    ]
                    if not user.stem_eligible and self._is_likely_stem(user.program or "")
                    else []
                ),
            ]

            if user.program_start_date and user.program_end_date:
                dates = self.date_engine.calculate(
                    program_start_date=user.program_start_date,
                    program_end_date=user.program_end_date,
                    stem_eligible=user.stem_eligible or False,
                    opt_start_date=user.opt_start_date,
                )

                context_lines.append(f"  Program Start: {user.program_start_date.isoformat()}")
                context_lines.append(f"  Program End: {user.program_end_date.isoformat()}")
                context_lines.append("")
                context_lines.append("CALCULATED DATES:")
                context_lines.append(f"  Current Status: {dates['current_status']}")
                context_lines.append(f"  CPT Eligible Date: {dates['cpt']['eligible_date']}")
                context_lines.append(f"  CPT Eligible Now: {'Yes' if dates['cpt']['is_eligible_now'] else 'No'}")
                context_lines.append(f"  OPT Apply Window Opens: {dates['opt']['apply_window_opens']}")
                context_lines.append(f"  OPT Apply Deadline: {dates['opt']['apply_deadline']}")
                if user.opt_start_date:
                    context_lines.append(f"  OPT Start Date (chosen): {user.opt_start_date.isoformat()}")
                else:
                    context_lines.append(f"  OPT Earliest Start: {dates['opt']['earliest_start_date']}")
                context_lines.append(f"  OPT End Date: {dates['opt']['end_date']}")
                context_lines.append(f"  OPT Grace Period Ends: {dates['opt']['grace_period_end']}")

                if dates["stem_opt"]:
                    context_lines.append(f"  STEM OPT Apply Window Opens: {dates['stem_opt']['apply_window_opens']}")
                    context_lines.append(f"  STEM OPT End Date: {dates['stem_opt']['end_date']}")
                    context_lines.append(f"  STEM OPT Grace Period Ends: {dates['stem_opt']['grace_period_end']}")
                    context_lines.append(f"  Total Work Authorization: {dates['stem_opt']['total_work_authorization_months']} months")

            return "\n".join(context_lines)
        finally:
            db.close()

    def _build_messages_with_history(
        self, question: str, chunks: list[dict], history: list[dict], user_context: str
    ) -> list[dict]:
        context = self.generator._build_context(chunks)

        current_message = ""
        if user_context:
            current_message += f"{user_context}\n\n"
        if context:
            current_message += f"CONTEXT:\n{context}\n\n"
        current_message += f"QUESTION:\n{question}"

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

    def chat(self, question: str, history: list[dict] = [], uid: str = None) -> dict:
        # Step 1 — classify intent and clean query
        rewrite = self.rewriter.classify(question)

        # Step 2 — detect OPT start date in message and save to DB
        if uid:
            opt_date = self._extract_opt_date(question)
            if opt_date:
                self._save_opt_start_date(uid, opt_date)

        # Step 3 — retrieve only if needed
        if rewrite["needs_retrieval"]:
            query = rewrite["cleaned_query"] or question
            chunks = self.retriever.retrieve(query)
            chunks = self.reranker.rerank(query, chunks)

            # Reranker quality gate
            MIN_RERANK_SCORE = 0.35
            if chunks and chunks[0].get("rerank_score", 1.0) < MIN_RERANK_SCORE:
                print(f"Reranker gate: BLOCKED — best score {chunks[0]['rerank_score']:.4f} below {MIN_RERANK_SCORE}")
                chunks = []
        else:
            chunks = []

        # Step 4 — build user context with personalized dates
        user_context = self._build_user_context(uid)

        # Step 5 — build messages with history and context
        messages = self._build_messages_with_history(question, chunks, history, user_context)

        # Step 6 — generate answer
        response = self.generator.client.messages.create(
            model=self.generator.MODEL,
            max_tokens=self.generator.MAX_TOKENS,
            system=self.generator.SYSTEM_PROMPT,
            messages=messages
        )

        answer = response.content[0].text

        # Step 7 — guardrails check
        guard = self.guardrails.check(answer, len(chunks), rewrite["intent"], has_user_context=bool(user_context))
        answer = guard["answer"]

        seen = set()
        unique_sources = []
        for c in chunks:
            key = f"{c['source']}_{c['category']}"
            if key not in seen:
                seen.add(key)
                unique_sources.append({
                    "source": c["source"],
                    "url": c["url"],
                    "category": c["category"],
                    "score": c["score"],
                })

        return {
            "question": question,
            "answer": answer,
            "intent": rewrite["intent"],
            "sources": unique_sources,
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