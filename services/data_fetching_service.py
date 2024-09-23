# services/data_fetching_service.py
import aiohttp
import ssl
import logging

logger = logging.getLogger(__name__)

class DataFetchingService:
    async def fetch_landing_page(self, url: str) -> bytes:
        # Create an SSL context that does not verify certificates
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

        logger.debug(f"Fetching URL {url} with SSL verification disabled")

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, ssl=ssl_context) as response:
                    if response.status == 200:
                        data = await response.read()
                        logger.info(f"Fetched data from {url}")
                        return data
                    else:
                        logger.error(f"Failed to fetch {url}, Status Code: {response.status}")
                        raise Exception(f"Failed to fetch {url}, Status Code: {response.status}")
            except aiohttp.ClientSSLError as ssl_err:
                logger.error(f"SSL error while fetching {url}: {ssl_err}")
                raise ssl_err
            except Exception as e:
                logger.error(f"Error while fetching {url}: {e}")
                raise e