from typing import Annotated, TypedDict, List, Dict, Optional
from agents.user_agent import UserAgent
from agents.product_manager_agent import ProductManagerAgent
from agents.ai_features_ideation_agent import AIFeatureIdeationAgent
from agents.developer_agent import DeveloperAgent
from agents.product_manager_agent import ProductManagerAgent
from services.RAGService import RAGService
from models.Evaluation import Evaluation

class EvaluationState(TypedDict, total=False):
    evaluation_scope: str
    user_agent: UserAgent
    rag_service: RAGService
    scenario: str
    product_info: str
    interaction_result: Dict
    evaluation: Evaluation
    evaluation_type: str
    product_manager_agent: ProductManagerAgent
    ai_feature_ideation_agent: AIFeatureIdeationAgent
    developer_agent: DeveloperAgent
    product_manager_agent: ProductManagerAgent
    product_id: int
    ideated_features: List[Dict]
    prioritized_features: List[Dict]
    feasibility_reports: Dict[str, Dict]
    final_report: str
