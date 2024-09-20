from fastapi import APIRouter, Depends, HTTPException, Form
from typing import Dict, Optional
from services.Evaluation import EvaluationService
from repositories.EvaluationRepository import EvaluationRepository
from services.RAGService import RAGService
from services.UserAgentService import UserAgentService
from agents.product_manager_agent import ProductManagerAgent
from agents.ai_features_ideation_agent import AIFeatureIdeationAgent
from agents.developer_agent import DeveloperAgent
from agents.user_agent import UserAgent
from database import transaction
from config import settings
from logging_config import setup_logging
import logging
from fastapi.encoders import jsonable_encoder

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/trigger-evaluation", response_model=Dict)
async def trigger_evaluation(
    name: str = Form(...),
    product_id: int = Form(...),
    user_agent_definition_id: int = Form(...),
    evaluation_type: str = Form(...),
    db_con=Depends(transaction),
):
    # Initialize repositories and services
    evaluation_repository = EvaluationRepository(db_con[0])
    rag_service = RAGService(vector_db=None)  # Assume vector DB is set up
    product_manager_agent = ProductManagerAgent(agent_characteristics=None)
    user_agent_service = UserAgentService(db_con[0])
    ai_feature_ideation_agent = AIFeatureIdeationAgent()
    developer_agent = DeveloperAgent()

    
    # Fetch user agent definition
    user_agent_definition = await user_agent_service.fetch_user_agent_definition(user_agent_definition_id)
    print("Printifn sample user agent definition", user_agent_definition)
    
    if not user_agent_definition:
        raise HTTPException(status_code=404, detail="User agent definition not found")
    
    # Access characteristics from the dictionary
    user_agent = UserAgent(agent_characteristics=user_agent_definition['characteristics'])
    
    # Initialize EvaluationService 
    evaluation_service = EvaluationService(
        evaluation_repository=evaluation_repository,
        rag_service=rag_service,
        product_manager_agent=product_manager_agent,
        user_agent=user_agent,
        ai_feature_ideation_agent=ai_feature_ideation_agent,
        developer_agent=developer_agent
    )
    
        # Create a new Evaluation and retrieve its ID
    evaluation_id = await evaluation_service.create_evaluation(name=name, product_id=product_id)
    logger.info("Created new evaluation with ID: %s", evaluation_id)
    
    # Trigger the workflow with the newly created evaluation_id
    result = await evaluation_service.trigger_workflow(
        evaluation_id=evaluation_id,
        evaluation_type=evaluation_type
    )
    logger.info("Triggered evaluation workflow with ID: %s", evaluation_id)

    return jsonable_encoder(result)