from models.Evaluation import Evaluation
from typing import List


class  EvaluationRepository:
    def __init__(self, db):
        self.db = db

    async def create(self, evaluation: Evaluation) -> int:
        query = """
        INSERT INTO evaluations (proj_id, name, status)
        VALUES (%s, %s, %s)
        """
        values = (
            evaluation.proj_id,
            evaluation.name,
            evaluation.status
        )
        await self.db.execute(query, values)
        return self.db.lastrowid

    async def get_by_id(self, evaluation_id: int) -> Evaluation:
        query = "SELECT * FROM evaluations WHERE id = %s"
        await self.db.execute(query, (evaluation_id,))
        result = await self.db.fetchone()
        if result:
            return Evaluation(**result)
        return None

    async def get_all(self) -> List[Evaluation]:
        query = "SELECT * FROM evaluations"
        await self.db.execute(query)
        results = await self.db.fetchall()
        return [Evaluation(**row) for row in results]

    async def update(self, evaluation: Evaluation) -> bool:
        query = """
        UPDATE evaluations
        SET proj_id = %s, name = %s, status = %s
        WHERE id = %s
        """
        values = (
            evaluation.proj_id,
            evaluation.name,
            evaluation.status,
            evaluation.id
        )
        await self.db.execute(query, values)
        return self.db.rowcount > 0

    async def delete(self, evaluation_id: int) -> bool:
        query = "DELETE FROM evaluations WHERE id = %s"
        await self.db.execute(query, (evaluation_id,))
        return self.db.rowcount > 0
