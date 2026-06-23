import hashlib
import json
from pathlib import Path


HASHES_FILE = Path("data/hashes/content_hashes.json")
SCRAPED_DIR = Path("data/scraped")


class HashChecker:
    """
    Manages content hashes for scraped pages.
    Detects changes so we only re-embed updated content.
    """

    def __init__(self, hashes_file: Path = HASHES_FILE):
        self.hashes_file = hashes_file
        self.hashes_file.parent.mkdir(parents=True, exist_ok=True)
        self.hashes = self._load()

    def _load(self) -> dict:
        if not self.hashes_file.exists():
            return {}
        with open(self.hashes_file, "r") as f:
            return json.load(f)

    def _save(self):
        with open(self.hashes_file, "w") as f:
            json.dump(self.hashes, f, indent=2)

    def _generate(self, content: str) -> str:
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    def has_changed(self, url: str, content: str) -> bool:
        new_hash = self._generate(content)
        old_hash = self.hashes.get(url)
        return old_hash != new_hash

    def update(self, url: str, content: str):
        self.hashes[url] = self._generate(content)
        self._save()

    def initialize_from_scraped(self):
        """
        First time setup — reads all existing scraped JSON files
        and generates hashes so future runs can detect changes.
        """
        if not SCRAPED_DIR.exists():
            print("No scraped data found.")
            return

        files = list(SCRAPED_DIR.glob("*.json"))

        if not files:
            print("No scraped files found.")
            return

        print(f"Initializing hashes from {len(files)} scraped files...")

        for filepath in files:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)

            url = data.get("url")
            content = data.get("content")

            if url and content:
                self.hashes[url] = self._generate(content)
                print(f" Hashed: {url}")

        self._save()
        print(f"\nHashes saved to: {self.hashes_file}")


if __name__ == "__main__":
    checker = HashChecker()
    checker.initialize_from_scraped()