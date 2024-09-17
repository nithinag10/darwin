from typing import List
import asyncio

class RAGService:
    def __init__(self, vector_db):
        self.vector_db = vector_db

    async def fetch_relevant_info(self, query: str, k: int = 5) -> List[str]:
        # Simulating vector database query
        await asyncio.sleep(0.5)  # Simulate DB query time
        return [f"Relevant info {i} for query: {query}" for i in range(k)]