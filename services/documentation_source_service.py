# services/documentation_source_service.py
from repositories.documentation_source_repository import DocumentationSourceRepository
from services.data_fetching_service import DataFetchingService
from services.blob_storage_service import BlobStorageService
from sqlalchemy.orm import Session
import logging

logger = logging.getLogger(__name__)

class DocumentationSourceService:
    def __init__(self, db: Session, blob_storage_service: BlobStorageService):
        self.db = db
        self.documentation_source_repo = DocumentationSourceRepository(db)
        self.data_fetching_service = DataFetchingService()
        self.blob_storage_service = blob_storage_service

    async def fetch_and_store_landing_page(self, product_id: int, url: str):
        # Fetch data
        data = await self.data_fetching_service.fetch_landing_page(url)
        content_type = "text/html"

        # Upload to Blob Storage
        blob_name = f"landing_pages/product_{product_id}/{self._generate_blob_name(url)}.html"
        storage_url = await self.blob_storage_service.upload_blob(blob_name, data, content_type)

        # Save metadata to DB
        documentation_source = DocumentationSource(
            product_id=product_id,
            type="landing_page",
            url=url,
            storage_url=storage_url,
            file_size=len(data),
            content_type=content_type,
            fetched_at=None,  # Update if needed
            created_at=None,   # ORM should handle default timestamps
            updated_at=None
        )
        documentation_source = self.documentation_source_repo.create_documentation_source(documentation_source)
        logger.info(f"Saved DocumentationSource ID: {documentation_source.id}")
        return documentation_source

    def _generate_blob_name(self, url: str) -> str:
        # Simple blob name generator based on URL
        return url.replace("https://", "").replace("http://", "").replace("/", "_")