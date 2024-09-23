from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any
from schemas.product_onboarding import ProductOnboardingRequest, ProductOnboardingResponse, OnboardingResult
from services.blob_storage_service import BlobStorageService
from services.product_onboarding_service import ProductOnboardingService
from database import get_db_conn, transaction
import os
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/product/onboard", response_model=ProductOnboardingResponse)
async def onboard_product(onboarding_request: ProductOnboardingRequest, db_con=Depends(transaction)):
    """
    Endpoint to onboard a new product.

    :param onboarding_request: Details required to onboard the product.
    :param db_transaction: Database transaction dependency.
    :return: Results of the onboarding process.
    """


            # Initialize BlobStorageService using environment variables
    blob_storage_service = BlobStorageService(
        connection_string=os.getenv('AZURE_STORAGE_CONNECTION_STRING'),
        container_name=os.getenv('AZURE_STORAGE_CONTAINER_NAME')
    )

    # Initialize ProductOnboardingService
    onboarding_service = ProductOnboardingService(db_con[0], blob_storage_service)

    # Prepare onboarding data
    onboarding_data = {
        "project_id": onboarding_request.project_id,
        "figma_file_name": onboarding_request.figma_file_name,
        "customer_info": onboarding_request.customer_info ,
        "figma_file_key" : onboarding_request.figma_file_key,
        "figma_token" : onboarding_request.figma_token
    }

    # Process onboarding
    sources = [source.model_dump() for source in onboarding_request.sources]  # Updated to use model_dump
    results_dict = await onboarding_service.onboard_product(onboarding_data, sources)

    # Format the results
    formatted_results = []
    for url, result in results_dict.items():
        formatted_result = OnboardingResult(
            url=url,
            status=result.get('status'),
            id=result.get('id'),
            storage_url=result.get('storage_url'),
            error=result.get('error')
        )
        formatted_results.append(formatted_result)

    return ProductOnboardingResponse(results=formatted_results)
