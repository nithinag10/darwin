from models.Evaluation import Evaluation, EvaluationStatus
from repositories.EvaluationRepository import EvaluationRepository
from services.RAGService import RAGService
from agents.project_manager_agent import ProjectManagerAgent
from agents.user_agent import UserAgent
from workflow.evaluation_workflow import run_evaluation_workflow
from typing import Optional


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

    async def change_evaluation_status(
        self, evaluation_id: int, new_status: EvaluationStatus
    ) -> Evaluation:
        evaluation = await self.evaluation_repository.get_by_id(evaluation_id)
        if not evaluation:
            raise ValueError("Evaluation not found")

        evaluation.status = new_status
        await self.evaluation_repository.update(evaluation)
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
        # Fetch the evaluation
        evaluation = await self.evaluation_repository.get_by_id(evaluation_id)
        if not evaluation:
            raise ValueError("Evaluation not found")

        # Trigger the LangGraph workflow
        workflow_result = await run_evaluation_workflow(
            evaluation, user_agent_definition_id, evaluation_type, self.rag_service,
            self.project_manager_agent, self.user_agent
        )

        # Update evaluation status based on workflow result
        if workflow_result:
            evaluation.status = EvaluationStatus.COMPLETED
            await self.evaluation_repository.update(evaluation)

        return workflow_result
