from typing import List
import asyncio

class RAGService:
    def __init__(self, vector_db):
        self.vector_db = vector_db

    async def fetch_relevant_info(self, product_id: int, k: int = 5) -> List[str]:
        """
        Fetch relevant information for a given product ID.
        
        For now, returns dummy data. Replace with actual implementation when ready.
        
        Args:
            product_id (int): The ID of the product.
            k (int): Number of relevant information items to fetch.

        Returns:
            List[str]: A list of dummy relevant information strings.
        """
        # Simulating vector database query
        await asyncio.sleep(0.5)  # Simulate DB query time
        return "Dummy product info. It has a login page with a username and password field. It also has a submit button."