# services/data_fetching_service.py
import aiohttp
import logging

logger = logging.getLogger(__name__)

class DataFetchingService:
    async def fetch_landing_page(self, url: str) -> bytes:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.read()
                        logger.info(f"Fetched data from {url}")
                        return data
                    else:
                        logger.error(f"Failed to fetch {url}, Status Code: {response.status}")
                        raise Exception(f"Failed to fetch {url}, Status Code: {response.status}")
        except Exception as e:
            logger.error(f"Error fetching landing page data from {url}: {e}")
            raise e