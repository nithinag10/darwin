from typing import List, Optional
from pydantic import BaseModel, Field

class LandingPageSource(BaseModel):
    type: str = Field(..., description="Type of the source (e.g., landing_page)")
    url: str = Field(..., description="URL of the landing page")

class ProductOnboardingRequest(BaseModel):
    user_id: int = Field(..., description="ID of the user onboarding the product")
    project_id: int = Field(..., description="ID of the associated project")
    figma_file_name: str = Field(..., description="Name of the Figma file")
    figma_file_key: str = Field(..., description="Key of the Figma file")
    figma_token: str = Field(..., description="Figma API token")
    sources: List[LandingPageSource] = Field(..., description="List of sources to process")
    customer_info: Optional[dict] = Field(None, description="Additional customer information")

class OnboardingResult(BaseModel):
    url: str
    status: str
    id: Optional[int] = None
    storage_url: Optional[str] = None
    error: Optional[str] = None

class ProductOnboardingResponse(BaseModel):
    results: List[OnboardingResult]