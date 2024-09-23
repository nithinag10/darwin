from typing import List, Dict, Any
import logging
from models.Product import Product
from repositories.ProductRepository import ProductRepository
from services.documentation_source_service import DocumentationSourceService
from pydantic import ValidationError

logger = logging.getLogger(__name__)

class ProductOnboardingService:
    def __init__(self, db, blob_storage_service):
        self.db = db
        self.product_repository = ProductRepository(db)
        self.documentation_source_service = DocumentationSourceService(db, blob_storage_service)

    async def onboard_product(self, onboarding_data: Dict[str, Any], sources: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Onboards a product by creating a product record and processing landing page sources.

        :param onboarding_data: Dictionary containing product and Figma details.
        :param sources: List of source dictionaries to process.
        :return: Dictionary with the results of each source processing.
        """
        results = {}
        product_id = None
        try:
            # Extract customer_info safely
            customer_info = onboarding_data.get("customer_info")
            if not isinstance(customer_info, dict):
                customer_info = {}
            custom_instructions = customer_info.get("custom_instructions", "")

            # 1. Create Product
            product = Product(
                project_id=onboarding_data["project_id"],
                name=onboarding_data["figma_file_name"],
                custom_instructions=custom_instructions  # Safely handled
            )
            product_id = await self.product_repository.create_product(product)
            logger.info(f"Created Product with ID: {product_id}")

            # 2. Process Each Source
            for source in sources:
                source_type = source.get('type')
                if source_type == 'landing_page':
                    url = source.get('url')
                    logger.debug(f"Source URL: {url} (type: {type(url)})")
                    
                    if isinstance(url, str):
                        url = url.strip()
                    else:
                        logger.warning(f"URL is not a string: {url} (type: {type(url)})")
                        results[source_type] = {'status': 'failed', 'error': 'URL must be a string'}
                        continue  # Skip processing this source

                    if url:
                        try:
                            doc_source_id = await self.documentation_source_service.fetch_and_store_landing_page(product_id, url)
                            results[url] = {'status': 'success', 'id': doc_source_id}
                        except ValidationError as ve:
                            logger.error(f"Validation error for URL {url}: {ve}")
                            results[url] = {'status': 'failed', 'error': 'Invalid URL format'}
                        except Exception as e:
                            logger.error(f"Failed to process landing page {url}: {e}")
                            results[url] = {'status': 'failed', 'error': str(e)}
                    else:
                        logger.warning(f"Empty URL provided for landing_page source: {source}")
                        results[source_type] = {'status': 'failed', 'error': 'Empty URL'}
                        
                else:
                    logger.warning(f"Unknown source type: {source_type}")
                    results[source_type] = {'status': 'failed', 'error': 'Unknown source type'}

            return results

        except Exception as e:
            logger.error(f"Error during product onboarding: {e}")
            raise e
        finally:
            # Ensure services are closed to prevent unclosed sessions
            await self.documentation_source_service.close_services()