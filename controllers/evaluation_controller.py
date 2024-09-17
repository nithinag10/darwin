from fastapi import APIRouter, Depends, HTTPException, Form
from typing import Dict
from services.Evaluation import EvaluationService
from repositories.EvaluationRepository import EvaluationRepository
from services.RAGService import RAGService
from agents.project_manager_agent import ProjectManagerAgent
from agents.user_agent import UserAgent
from database import transaction
from models.Evaluation import EvaluationStatus
from config import settings
import aiomysql

router = APIRouter()

@router.post("/trigger-evaluation", response_model=Dict)
async def trigger_evaluation(
    evaluation_id: int = Form(...),
    user_agent_definition_id: int = Form(...),
    evaluation_type: str = Form(...),
    db_con=Depends(transaction)
):
    # Initialize repositories and services
    evaluation_repository = EvaluationRepository(db_con[0])
    rag_service = RAGService(vector_db=None)  # Assume vector DB is set up
    project_manager_agent = ProjectManagerAgent()
    
    # Fetch user agent definition
    # You may need to implement UserAgentDefinitionRepository to fetch the definition
    # For simplicity, assume we have a method to get characteristics by ID
    user_agent_definition = await fetch_user_agent_definition(user_agent_definition_id, db_con[0])
    
    if not user_agent_definition:
        raise HTTPException(status_code=404, detail="User agent definition not found")
    
    user_agent = UserAgent(agent_characteristics=user_agent_definition.characteristics)
    
    # Initialize EvaluationService
    evaluation_service = EvaluationService(
        evaluation_repository=evaluation_repository,
        rag_service=rag_service,
        project_manager_agent=project_manager_agent,
        user_agent=user_agent
    )
    
    try:
        result = await evaluation_service.trigger_workflow(
            evaluation_id=evaluation_id,
            user_agent_definition_id=user_agent_definition_id,
            evaluation_type=evaluation_type
        )
        return {"status": "success", "result": result}
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def fetch_user_agent_definition(user_agent_definition_id: int, db_con) -> Optional[Dict]:
    query = "SELECT * FROM UserAgentDefinitions WHERE id = %s AND is_predefined = TRUE;"
    async with db_con.cursor(aiomysql.DictCursor) as cur:
        await cur.execute(query, (user_agent_definition_id,))
        row = await cur.fetchone()
        return row if row else None