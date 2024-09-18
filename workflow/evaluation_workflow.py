from langgraph.graph import StateGraph
from typing import Dict, TypedDict
from agents.project_manager_agent import ProjectManagerAgent
from agents.user_agent import UserAgent
from services.RAGService import RAGService
from models.Evaluation import Evaluation


class EvaluationState(TypedDict):
    evaluation_scope: str
    user_agent: UserAgent
    rag_service: RAGService
    scenario: str
    product_info: str
    interaction_result: str


async def define_scope(state: EvaluationState) -> EvaluationState:
    evaluation = state.get('evaluation')
    project_manager = state['project_manager_agent']
    state["evaluation_scope"] = await project_manager.define_evaluation_scope(
        f"Evaluation ID: {evaluation.id}, Type: {state['evaluation_type']}"
    )
    return state


async def fetch_product_info(state: EvaluationState) -> EvaluationState:
    state["product_info"] = await state["rag_service"].fetch_relevant_info(state["evaluation_scope"])
    return state


async def simulate_user_interaction(state: EvaluationState) -> EvaluationState:
    state["interaction_result"] = await state["user_agent"].simulate_interaction(
        state["scenario"], state["product_info"]
    )
    return state


async def run_evaluation_workflow(
    evaluation: Evaluation,
    user_agent_definition_id: int,
    evaluation_type: str,
    rag_service: RAGService,
    project_manager_agent: ProjectManagerAgent,
    user_agent: UserAgent
) -> Dict:
    # Initialize workflow with updated Graph configuration if needed
    workflow = Graph()

    # Define nodes (ensure methods are correctly registered)
    workflow.add_node("define_scope", define_scope)
    workflow.add_node("fetch_product_info", fetch_product_info)
    workflow.add_node("simulate_user_interaction", simulate_user_interaction)

    # Define edges (verify if edge definition syntax has changed)
    workflow.add_edge("define_scope", "fetch_product_info")
    workflow.add_edge("fetch_product_info", "simulate_user_interaction")

    # Initialize state
    initial_state: EvaluationState = {
        "evaluation": evaluation,
        "evaluation_type": evaluation_type,
        "user_agent": user_agent,
        "rag_service": rag_service,
        "project_manager_agent": project_manager_agent,
        "scenario": "First-time user exploring the product",
        "evaluation_scope": "",
        "product_info": "",
        "interaction_result": ""
    }

    # Run the workflow (ensure asynchronous streaming is handled as per latest API)
    async for state in workflow.astream(initial_state):
        if workflow.is_finished():
            return state

    return {}