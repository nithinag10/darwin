from fastapi import APIRouter, Depends, HTTPException
from typing import List
from models.UserAgentDefinition import UserAgentDefinition
from services.UserAgentService import UserAgentService
from repositories.UserAgentDefinitionRepository import UserAgentDefinitionRepository
from database import transaction

router = APIRouter()

@router.post("/user-agents", response_model=UserAgentDefinition)
async def create_user_agent(user_agent: UserAgentDefinition, db_con=Depends(transaction)):
    user_agent_repository = UserAgentDefinitionRepository(db_con[0])
    user_agent_service = UserAgentService(user_agent_repository)
    return await user_agent_service.create_user_agent(user_agent)

@router.get("/user-agents", response_model=List[UserAgentDefinition])
async def get_predefined_user_agents(db_con=Depends(transaction)):
    user_agent_repository = UserAgentDefinitionRepository(db_con[0])
    user_agent_service = UserAgentService(user_agent_repository)
    return await user_agent_service.get_all_predefined_agents()
