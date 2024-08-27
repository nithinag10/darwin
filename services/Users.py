from repositories.UserRepository import UserRepository
from models.User import User
from typing import Optional, Dict
import bcrypt
import jwt
from datetime import datetime, timedelta

class UserService:
    def __init__(self, db_con, secret_key):
        self.user_repository = UserRepository(db_con)
        self.secret_key = secret_key

    async def create_user(self, name: str, email: str, password: str) -> Optional[Dict]:
        # Check if user already exists
        existing_user = await self.user_repository.get_user_by_email(email)
        if existing_user:
            return None

        # Hash the password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        # Create the user
        user = User(name=name, email=email, password=hashed_password.decode('utf-8'))
        user_id = await self.user_repository.create_user(user)


        # Fetch the created user
        user_data = await self.user_repository.get_user_by_id(user_id)
        if not user_data:
            return None

        # Generate token
        token = self._generate_token(user_data)

        return {"user": User(**user_data), "token": token}

    async def login(self, email: str, password: str) -> Optional[Dict]:
        user_data = await self.user_repository.get_user_by_email(email)
        if not user_data:
            return None

        if bcrypt.checkpw(password.encode('utf-8'), user_data['password'].encode('utf-8')):
            # Generate token
            token = self._generate_token(user_data)
            return {"user": User(**user_data), "token": token}
        else:
            return None

    def _generate_token(self, user_data: Dict) -> str:
        payload = {
            'user_id': user_data['id'],
            'email': user_data['email'],
            'exp': datetime.utcnow() + timedelta(days=1)  # Token expires in 1 day
        }
        return jwt.encode(payload, self.secret_key, algorithm='HS256')


