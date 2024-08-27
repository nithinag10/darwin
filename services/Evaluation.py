from models.Evaluation import Evaluation, EvaluationStatus
from repositories.EvaluationRepository import EvaluationRepository


class EvaluationService:
    def __init__(self, evaluation_repository: EvaluationRepository):
        self.evaluation_repository = evaluation_repository

    async def start_evaluation(self, evaluation_id: int) -> Evaluation:
        evaluation = await self.evaluation_repository.get_by_id(evaluation_id)
        if evaluation:
            evaluation.status = EvaluationStatus.START
            await self.evaluation_repository.update(evaluation)
        return evaluation

    async def set_evaluation_in_progress(self, evaluation_id: int) -> Evaluation:
        evaluation = await self.evaluation_repository.get_by_id(evaluation_id)
        if evaluation:
            evaluation.status = EvaluationStatus.IN_PROGRESS
            await self.evaluation_repository.update(evaluation)
        return evaluation

    async def complete_evaluation(self, evaluation_id: int) -> Evaluation:
        evaluation = await self.evaluation_repository.get_by_id(evaluation_id)
        if evaluation:
            evaluation.status = EvaluationStatus.COMPLETED
            await self.evaluation_repository.update(evaluation)
        return evaluation
