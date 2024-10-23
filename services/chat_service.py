import uuid
from typing import List, Dict, Optional
import aiomysql

class ChatService:
    def __init__(self, db_connection):
        self.db = db_connection

    async def save_chat_session(self, persona_id: int, business_idea: str, initial_prompt: str, initial_response: str) -> int:
        query = """
        INSERT INTO chat_sessions (persona_id, business_idea, initial_prompt, initial_response)
        VALUES (%s, %s, %s, %s)
        """
        cursor = await self.db.cursor()
        try:
            await cursor.execute(query, (persona_id, business_idea, initial_prompt, initial_response))
            await self.db.commit()
            return cursor.lastrowid
        finally:
            await cursor.close()

    async def save_chat_message(self, session_id: int, content: str, is_user: bool):
        query = """
        INSERT INTO chat_messages (session_id, content, is_user)
        VALUES (%s, %s, %s)
        """
        cursor = await self.db.cursor()
        try:
            await cursor.execute(query, (session_id, content, is_user))
            await self.db.commit()
        finally:
            await cursor.close()

    async def get_chat_history(self, session_id: int) -> List[Dict]:
        query = """
        SELECT cs.initial_prompt, cm.content, cm.is_user, cm.timestamp
        FROM chat_sessions cs
        LEFT JOIN chat_messages cm ON cs.session_id = cm.session_id
        WHERE cs.session_id = %s
        ORDER BY cm.timestamp
        """
        cursor = await self.db.cursor()
        try:
            await cursor.execute(query, (session_id,))
            rows = await cursor.fetchall()
            
            history = []
            if rows:
                # Add initial prompt as the first message
                history.append({"content": rows[0][0], "is_user": False})
                
                # Add subsequent messages
                for row in rows:
                    if row[1] is not None:  # Check if content is not None
                        history.append({"content": row[1], "is_user": bool(row[2])})
            
            return history
        finally:
            await cursor.close()

    async def get_chat_session(self, session_id: int) -> Optional[Dict]:
        query = """
        SELECT persona_id, business_idea, initial_prompt, initial_response
        FROM chat_sessions
        WHERE session_id = %s
        """
        cursor = await self.db.cursor()
        try:
            await cursor.execute(query, (session_id,))
            result = await cursor.fetchone()
            if result:
                return {
                    "persona_id": result[0],
                    "business_idea": result[1],
                    "initial_prompt": result[2],
                    "initial_response": result[3]
                }
            return None
        finally:
            await cursor.close()
