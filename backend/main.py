from fastapi import FastAPI
from config import settings
from utils.logger import get_logger
from agent_manager import AgentManager
from routes import risk, route, emergency, user

logger = get_logger("Main")

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
)

agent_manager = AgentManager()

# Register routers
app.include_router(risk.router, prefix="/api")
app.include_router(route.router, prefix="/api")
app.include_router(emergency.router, prefix="/api")
app.include_router(user.router, prefix="/api")


@app.get("/health")
def health_check():
    return {"status": "ok", "service": settings.APP_NAME}


@app.post("/api/analyze")
def analyze(payload: dict):
    """
    Unified endpoint to test agent orchestration flow.
    """
    logger.info("Received analysis request")
    return agent_manager.run(payload)

