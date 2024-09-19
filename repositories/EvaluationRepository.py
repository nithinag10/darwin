from models.Evaluation import Evaluation, EvaluationStatus
from typing import Optional
from datetime import datetime
import aiomysql  # Added import


class EvaluationRepository:
    def __init__(self, db_con):
        self.db_con = db_con

    async def get_by_id(self, evaluation_id: int) -> Optional[Evaluation]:
        query = "SELECT * FROM Evaluations WHERE id = %s;"
        async with self.db_con.cursor(aiomysql.DictCursor) as cur:
            await cur.execute(query, (evaluation_id,))
            row = await cur.fetchone()
            if row:
                return Evaluation(**row)
        return None

    async def update(self, evaluation: Evaluation) -> bool:
        query = """
        UPDATE Evaluations 
        SET status = %s, updated_at = NOW()
        WHERE id = %s;
        """
        async with self.db_con.cursor() as cur:
            await cur.execute(query, (evaluation.status.value, evaluation.id))
            return cur.rowcount > 0

    async def create(self, evaluation: Evaluation) -> int:
        print("Printing the status: " + str(evaluation.status))
        # Ensure the status is valid
        if evaluation.status not in EvaluationStatus:  # Check against the enum directly
            raise ValueError("Invalid status: " + str(evaluation.status))
        
        query = """
        INSERT INTO Evaluations (name, status, created_at, updated_at, product_id)
        VALUES (%s, %s, NOW(), NOW(), %s);
        """
        async with self.db_con.cursor() as cur:
            await cur.execute(query, (evaluation.name, evaluation.status.value, evaluation.product_id))  # Use .value to get the string
            return cur.lastrowid  # Use lastrowid to get the last inserted ID