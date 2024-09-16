from fastapi import APIRouter, Depends, Form, HTTPException
from typing import Dict, Union
from services.Users import UserService
from models.User import User
from database import get_db_conn, transaction
from config import settings

router = APIRouter()

@router.post("/signup", response_model=Dict[str, Union[User, str]])
async def signup(name: str = Form(...), email: str = Form(...), password: str = Form(...), db_con=Depends(transaction)):
    user_service = UserService(db_con[0], settings.secret_key)  # Use the connection from the transaction
    result = await user_service.create_user(name, email, password)
    if result:
        return {"user": result["user"], "token": result["token"]}
    else:
        raise HTTPException(status_code=400, detail="User already exists")

@router.post("/login", response_model=Dict[str, Union[User, str]])
async def login(email: str = Form(...), password: str = Form(...), db_con=Depends(transaction)):
    user_service = UserService(db_con[0], settings.secret_key)  # Use the connection from the transaction
    result = await user_service.login(email, password)
    if result:
        return {"user": result["user"], "token": result["token"]}
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials")
