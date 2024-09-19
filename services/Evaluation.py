from models.Evaluation import Evaluation, EvaluationStatus
from repositories.EvaluationRepository import EvaluationRepository
from services.RAGService import RAGService
from agents.project_manager_agent import ProjectManagerAgent
from agents.user_agent import UserAgent
from workflow.evaluation_workflow import run_evaluation_workflow
from typing import Optional

import logging
from logging_config import setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

class EvaluationService:
    def __init__(
        self,
        evaluation_repository: EvaluationRepository,
        rag_service: RAGService,
        project_manager_agent: ProjectManagerAgent,
        user_agent: UserAgent
    ):
        self.evaluation_repository = evaluation_repository
        self.rag_service = rag_service
        self.project_manager_agent = project_manager_agent
        self.user_agent = user_agent

    async def create_evaluation(self, name: str, product_id: int) -> int:
        logger.debug("Creating new evaluation with name: %s and product_id: %s", name, product_id)
        new_evaluation = Evaluation(
            name=name,
            status=EvaluationStatus.START,
            product_id=product_id
        )
        evaluation_id = await self.evaluation_repository.create(new_evaluation)
        logger.debug("Created evaluation with ID: %s", evaluation_id)
        return evaluation_id

    async def change_evaluation_status(
        self, evaluation_id: int, new_status: EvaluationStatus
    ) -> Evaluation:
        logger.debug("Changing evaluation status for ID: %s to %s", evaluation_id, new_status)
        evaluation = await self.evaluation_repository.get_by_id(evaluation_id)
        if not evaluation:
            logger.error("Evaluation not found for ID: %s", evaluation_id)
            raise ValueError("Evaluation not found")

        evaluation.status = new_status
        await self.evaluation_repository.update(evaluation)
        logger.debug("Successfully changed evaluation status for ID: %s", evaluation_id)
        return evaluation

    async def start_evaluation_status(self, evaluation_id: int) -> Evaluation:
        return await self.change_evaluation_status(evaluation_id, EvaluationStatus.START)

    async def set_evaluation_in_progress(self, evaluation_id: int) -> Evaluation:
        return await self.change_evaluation_status(evaluation_id, EvaluationStatus.IN_PROGRESS)

    async def complete_evaluation(self, evaluation_id: int) -> Evaluation:
        return await self.change_evaluation_status(evaluation_id, EvaluationStatus.COMPLETED)

    async def trigger_workflow(
        self, evaluation_id: int, user_agent_definition_id: int, evaluation_type: str
    ) -> Optional[dict]:
        logger.info("Starting evaluation workflow for ID: %s", evaluation_id)
        # Fetch the evaluation
        evaluation = await self.evaluation_repository.get_by_id(evaluation_id)
        if not evaluation:
            logger.error("Evaluation not found for ID: %s", evaluation_id)
            raise ValueError("Evaluation not found")

        logger.debug("Triggering workflow for evaluation ID: %s", evaluation_id)
        # Trigger the LangGraph workflow
        workflow_result = await run_evaluation_workflow(
            evaluation, evaluation_type, self.rag_service,
            self.project_manager_agent, self.user_agent
        )

        # Update evaluation status based on workflow result
        if workflow_result:
            evaluation.status = EvaluationStatus.COMPLETED
            await self.evaluation_repository.update(evaluation)
            logger.debug("Workflow completed for evaluation ID: %s", evaluation_id)

        return workflow_result
