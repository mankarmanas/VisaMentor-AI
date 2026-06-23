import httpx
import json
import time
from bs4 import BeautifulSoup
from datetime import datetime, timezone
from pathlib import Path
from src.utils.hash_checker import HashChecker


SCRAPED_DIR = Path("data/scraped")

SOURCES = [
    {
        "url": "https://www.uscis.gov/working-in-the-united-states/students-and-exchange-visitors/students-and-employment",
        "source": "USCIS",
        "category": "F1_employment",
    },
    {
        "url": "https://www.uscis.gov/working-in-the-united-states/students-and-exchange-visitors/optional-practical-training-opt-for-f-1-students",
        "source": "USCIS",
        "category": "OPT",
    },
    {
        "url": "https://www.uscis.gov/working-in-the-united-states/students-and-exchange-visitors/optional-practical-training-extension-for-stem-students-stem-opt",
        "source": "USCIS",
        "category": "STEM_OPT",
    },
    {
        "url": "https://www.uscis.gov/working-in-the-united-states/students-and-exchange-visitors/students-and-employment/changing-to-a-nonimmigrant-f-or-m-student-status",
        "source": "USCIS",
        "category": "F1_status_change",
    },
    {
        "url": "https://www.uscis.gov/policy-manual/volume-2-part-f",
        "source": "USCIS",
        "category": "policy_manual",
    },
    {
        "url": "https://studyinthestates.dhs.gov/students/training-opportunities-in-the-united-states",
        "source": "SEVP",
        "category": "training_opportunities",
    },
    {
        "url": "https://studyinthestates.dhs.gov/stem-opt-hub",
        "source": "SEVP",
        "category": "STEM_OPT",
    },
    {
        "url": "https://www.ice.gov/sevis/practical-training",
        "source": "ICE",
        "category": "practical_training",
    },
]


class TextCleaner:
    """Extracts clean text from raw HTML."""

    @staticmethod
    def clean(html: str) -> tuple[str, str]:
        soup = BeautifulSoup(html, "html.parser")

        for tag in soup(["script", "style", "nav", "footer", "header", "aside", "form"]):
            tag.decompose()

        title = soup.find("title")
        title_text = title.get_text(strip=True) if title else ""

        main = (
            soup.find("main")
            or soup.find("article")
            or soup.find("div", {"id": "main-content"})
            or soup.body
        )

        raw_text = main.get_text(separator="\n", strip=True) if main else soup.get_text(separator="\n", strip=True)
        lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
        content = "\n".join(lines)

        return title_text, content


class WebScraper:
    """Scrapes government websites and saves structured JSON output."""

    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
    }

    def __init__(self, output_dir: Path = SCRAPED_DIR, delay: int = 2):
        self.output_dir = output_dir
        self.delay = delay
        self.cleaner = TextCleaner()
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def scrape_url(self, source: dict) -> dict | None:
        url = source["url"]
        print(f"\nScraping: {url}")

        try:
            with httpx.Client(headers=self.HEADERS, timeout=30, follow_redirects=True) as client:
                response = client.get(url)

            if response.status_code != 200:
                print(f" Failed — HTTP {response.status_code}")
                return None

            title, content = self.cleaner.clean(response.text)

            if not content.strip():
                print(f" Empty content — skipping")
                return None

            print(f" Success — {len(content)} characters")

            return {
                "url": url,
                "source": source["source"],
                "category": source["category"],
                "title": title,
                "content": content,
                "scraped_at": datetime.now(timezone.utc).isoformat(),
            }

        except Exception as e:
            print(f" Error - {e}")
            return None

    def save(self, data: dict):
        slug = data["url"].rstrip("/").split("/")[-1][:50]
        filename = f"{data['source'].lower()}_{slug}.json"
        filepath = self.output_dir / filename

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f" Saved: {filepath}")

    def run(self, sources: list[dict]):

        print("=" * 20)
        print("Starting Visa Mentor AI Web Scraper")
        print("=" * 20)

        checker = HashChecker()
        success, failed , skipped = 0, 0, 0

        for source in sources:
            result = self.scrape_url(source)

            if result:
                if checker.has_changed(result["url"],result["content"]):
                    self.save(result)
                    checker.update(result["url"], result["content"])
                    success += 1
                else:
                    print(f"No changes detected — skipping")
                    skipped += 1
            else:
                failed += 1

            time.sleep(self.delay)

        print("\n" + "=" * 50)
        print(f"Done! Success: {success} | Skipped: {skipped} | Failed: {failed}")
        print(f"Files saved to: {self.output_dir}")
        print("=" * 50)


if __name__ == "__main__":
    scraper = WebScraper()
    scraper.run(SOURCES)