from fastapi import FastAPI
from controllers.user_controller import router as user_router
from controllers.user_agent_controller import router as user_agent_router
from controllers.evaluation_controller import router as evaluation_router

app = FastAPI()

app.include_router(user_router)
app.include_router(user_agent_router)
app.include_router(evaluation_router)

@app.get("/")
async def root():
    return {"message": "Hello World"}