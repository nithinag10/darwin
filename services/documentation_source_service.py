# services/documentation_source_service.py
from repositories.DocumentationSourceRepository import DocumentationSourceRepository
from services.data_fetching_service import DataFetchingService
from services.blob_storage_service import BlobStorageService
from models.documentation_source import DocumentationSourceSchema
from pydantic import ValidationError
import logging
import html2text
import json

logger = logging.getLogger(__name__)

class DocumentationSourceService:
    def __init__(self, db, blob_storage_service: BlobStorageService):
        self.db = db
        self.documentation_source_repo = DocumentationSourceRepository(db)
        self.data_fetching_service = DataFetchingService()
        self.blob_storage_service = blob_storage_service

    async def fetch_and_store_landing_page(self, product_id: int, url: str):
        logger.debug(f"Processing URL: {url} (type: {type(url)})")

        # Fetch data
        try:
            data = await self.data_fetching_service.fetch_landing_page(url)
            logger.debug(f"Fetched data length: {len(data)} bytes from {url}")
        except Exception as e:
            logger.error(f"Failed to fetch data from {url}: {e}")
            raise e

        content_type = "text/html"

        # Convert HTML to plain text
        try:
            html_content = data.decode('utf-8', errors='ignore')  # Handle decoding errors
            text_maker = html2text.HTML2Text()
            text_maker.ignore_links = True  # Optional: ignore links in the text output
            text_content = text_maker.handle(html_content)
            text_data = text_content.encode('utf-8')

            logger.debug(f"Converted text content length: {len(text_data)} bytes from {url}")

            if not text_data.strip():
                logger.warning(f"Empty text_content after conversion for URL: {url}")
                # Optionally, handle empty text_content by storing original HTML or retrying
                # For example, store original HTML if text_content is empty
                blob_name = f"landing_pages/product_{product_id}/{self._generate_blob_name(url)}.html"
                storage_url = await self.blob_storage_service.upload_blob(blob_name, data, content_type)
                logger.info(f"Stored original HTML for URL: {url} due to empty text_content")
                
                content_type = "text/html"  # Content remains HTML
                documentation_source = DocumentationSourceSchema(
                    product_id=product_id,
                    type="landing_page",
                    url=str(url),  # Ensure this is a string
                    storage_url=storage_url,
                    file_size=len(data),
                    content_type=content_type,
                    fetched_at=None,
                    created_at=None,
                    updated_at=None
                )

                documentation_source_id = await self.documentation_source_repo.create(documentation_source)
                logger.info(f"Saved DocumentationSource ID (HTML stored): {documentation_source_id}")
                return documentation_source_id

        except Exception as e:
            logger.error(f"Error converting HTML to text for URL {url}: {e}")
            raise e

        # Upload to Blob Storage
        try:
            blob_name = f"landing_pages/product_{product_id}/{self._generate_blob_name(url)}.txt"
            storage_url = await self.blob_storage_service.upload_blob(blob_name, text_data, "text/plain")
            logger.info(f"Uploaded text content to Blob Storage for URL: {url}")
        except Exception as e:
            logger.error(f"Failed to upload text data for URL {url}: {e}")
            raise e

        # Save metadata to DB
        try:
            documentation_source = DocumentationSourceSchema(
                product_id=product_id,
                type="landing_page",
                url=str(url),  # Ensure this is a string
                storage_url=storage_url,
                file_size=len(text_data),
                content_type="text/plain",
                fetched_at=None,
                created_at=None,
                updated_at=None
            )
        except ValidationError as ve:
            logger.error(f"Pydantic validation error: {ve}")
            raise ve

        try:
            documentation_source_id = await self.documentation_source_repo.create(documentation_source)
            logger.info(f"Saved DocumentationSource ID: {documentation_source_id}")
            return documentation_source_id
        except Exception as e:
            logger.error(f"Failed to save DocumentationSource to DB for URL {url}: {e}")
            raise e

    async def fetch_and_store_figma_design(self, product_id: int, figma_token: str, file_key: str):
        """
        Fetches and stores Figma design data.
        
        :param product_id: ID of the product.
        :param figma_token: Your Figma API token.
        :param file_key: The Figma file key.
        :return: ID of the saved DocumentationSource record.
        """
        logger.debug(f"Processing Figma file: {file_key} for product ID: {product_id}")

        # Fetch Figma data
        try:
            data = await self.data_fetching_service.fetch_figma_design(figma_token, file_key)
            logger.debug(f"Fetched Figma data for file key: {file_key}")
        except Exception as e:
            logger.error(f"Failed to fetch Figma data for file key {file_key}: {e}")
            raise e

        content_type = "application/json"

        # Serialize Figma data to JSON
        try:
            json_data = json.dumps(data, indent=2).encode('utf-8')
            logger.debug(f"Serialized Figma data length: {len(json_data)} bytes for file key: {file_key}")
        except Exception as e:
            logger.error(f"Error serializing Figma data for file key {file_key}: {e}")
            raise e

        # Upload to Blob Storage
        try:
            blob_name = f"figma_designs/product_{product_id}/{self._generate_blob_name(file_key)}.json"
            storage_url = await self.blob_storage_service.upload_blob(blob_name, json_data, content_type)
            logger.info(f"Uploaded Figma design to Blob Storage: {storage_url}")
        except Exception as e:
            logger.error(f"Failed to upload Figma data for file key {file_key}: {e}")
            raise e

        # Save metadata to DB
        try:
            documentation_source = DocumentationSourceSchema(
                product_id=product_id,
                type="figma_design",
                url=f"https://www.figma.com/file/{file_key}",
                storage_url=storage_url,
                file_size=len(json_data),
                content_type=content_type,
                fetched_at=None,
                created_at=None,
                updated_at=None
            )
        except ValidationError as ve:
            logger.error(f"Pydantic validation error: {ve}")
            raise ve

        try:
            documentation_source_id = await self.documentation_source_repo.create(documentation_source)
            logger.info(f"Saved DocumentationSource ID: {documentation_source_id}")
            return documentation_source_id
        except Exception as e:
            logger.error(f"Failed to save DocumentationSource to DB for file key {file_key}: {e}")
            raise e

    def _generate_blob_name(self, identifier: str) -> str:
        """
        Generates a blob name based on a URL or file key.

        :param identifier: URL or file key.
        :return: Sanitized blob name string.
        """
        return identifier.replace("https://", "").replace("http://", "").replace("/", "_").replace(".", "_")

    async def close_services(self):
        await self.blob_storage_service.close()
        logger.info("Closed BlobStorageService")