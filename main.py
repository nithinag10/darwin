from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.requests import Request
from fastapi.templating import Jinja2Templates
from controllers.user_controller import router as user_router
from controllers.user_agent_controller import router as user_agent_router
from controllers.evaluation_controller import router as evaluation_router
from controllers.onboard_product import router as product_onboarding_router

app = FastAPI()

templates = Jinja2Templates(directory="templates")

app.include_router(user_router, prefix="/api/users")
app.include_router(user_agent_router)
app.include_router(evaluation_router)
app.include_router(product_onboarding_router, prefix="/api")

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    print('Request for index page received')
    return templates.TemplateResponse('index.html', {"request": request})