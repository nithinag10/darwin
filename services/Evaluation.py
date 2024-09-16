from models.Evaluation import Evaluation, EvaluationStatus
from repositories.EvaluationRepository import EvaluationRepository


class EvaluationService:
    def __init__(self, evaluation_repository: EvaluationRepository):
        self.evaluation_repository = evaluation_repository

    async def change_evaluation_status(self, evaluation_id: int, new_status: EvaluationStatus) -> Evaluation:
        evaluation = await self.evaluation_repository.get_by_id(evaluation_id)
        if evaluation:
            evaluation.status = new_status
            await self.evaluation_repository.update(evaluation)
        return evaluation

    async def start_evaluation_status(self, evaluation_id: int) -> Evaluation:
        return await self.change_evaluation_status(evaluation_id, EvaluationStatus.START)

    async def set_evaluation_in_progress(self, evaluation_id: int) -> Evaluation:
        return await self.change_evaluation_status(evaluation_id, EvaluationStatus.IN_PROGRESS)

    async def complete_evaluation(self, evaluation_id: int) -> Evaluation:
        return await self.change_evaluation_status(evaluation_id, EvaluationStatus.COMPLETED)
