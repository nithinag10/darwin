from typing import Annotated, TypedDict
from agents.user_agent import UserAgent
from agents.project_manager_agent import ProjectManagerAgent
from services.RAGService import RAGService
from models.Evaluation import Evaluation

class EvaluationState(TypedDict):
    evaluation_scope: str
    user_agent: UserAgent
    rag_service: RAGService
    scenario: str
    product_info: str
    interaction_result: str
    evaluation: Evaluation
    evaluation_type: str
    project_manager_agent: ProjectManagerAgent
    product_id: int
