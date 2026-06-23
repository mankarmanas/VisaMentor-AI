from pinecone import Pinecone, ServerlessSpec
import os
from dotenv import load_dotenv

load_dotenv()

pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

print("Deleting old index...")
pc.delete_index("visa-mentor-ai")
print("Deleted.")

print("Creating new index with dotproduct metric...")
pc.create_index(
    name="visa-mentor-ai",
    dimension=3072,
    metric="dotproduct",
    spec=ServerlessSpec(
        cloud="aws",
        region="us-east-1"
    )
)
print("Done. New index created.")