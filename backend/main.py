from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import settings
from utils.logger import get_logger
from agent_manager import AgentManager
from schemas import AnalyzeRequest, AnalyzeResponse
from routes import risk, route, emergency, user
from utils.security import rate_limit, verify_session_token
from utils.storage import init_db

logger = get_logger("Main")

@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

agent_manager = AgentManager()
protected_dependencies = [Depends(verify_session_token), Depends(rate_limit)]
public_api_dependencies = [Depends(rate_limit)]

# Register routers
app.include_router(risk.router, prefix="/api", dependencies=protected_dependencies)
app.include_router(route.router, prefix="/api", dependencies=protected_dependencies)
app.include_router(emergency.router, prefix="/api", dependencies=protected_dependencies)
app.include_router(user.router, prefix="/api", dependencies=public_api_dependencies)

logger.info(f"NETRIKAN API initialized - v{settings.APP_VERSION}")


@app.get("/health")
def health_check():
    return {"status": "ok", "service": settings.APP_NAME}


@app.post("/api/analyze", response_model=AnalyzeResponse, dependencies=protected_dependencies)
def analyze(payload: AnalyzeRequest):
    """
    Unified endpoint to test agent orchestration flow.
    Processes location and contextual data through all agents.
    """
    logger.info("Received analysis request")
    return agent_manager.run(payload.model_dump())


if __name__ == "__main__":
    import uvicorn
    logger.info(f"Starting {settings.APP_NAME} server on {settings.HOST}:{settings.PORT}")
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD,
        log_level="info"
    )
