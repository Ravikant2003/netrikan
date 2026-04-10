from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from config import settings
from utils.logger import get_logger
from core.orchestrator import safety_app
from schemas import AnalyzeRequest, AnalyzeResponse, RouteRequest, SimulationRequest
from utils.maps_api import get_multiple_routes
from simulation.scenarios import get_scenario_steps, list_scenarios
from services.incidents import incident_manager
from services.ws_manager import ws_manager


logger = get_logger("Netrikan-Core")

@asynccontextmanager
async def lifespan(_: FastAPI):
    logger.info("Initializing Netrikan 3-Layer Agentic Architecture with LangGraph")
    yield

app = FastAPI(
    title=f"{settings.APP_NAME} (LangGraph)",
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

@app.get("/health")
def health_check():
    return {"status": "ok", "architecture": "3-layer-langgraph"}

@app.post("/api/analyze")
async def analyze(payload: AnalyzeRequest):
    """
    Unified entry point powered by LangGraph.
    Executes the 3-layer workflow: Monitoring -> Reasoning -> Action.
    """
    logger.info("New analysis request received via LangGraph")
    
    # Initial state for the graph
    initial_state = {
        "payload": payload.model_dump(),
        "status": "started"
    }
    
    # Invoke the LangGraph workflow
    final_state = await safety_app.ainvoke(initial_state)

    # PRD-style incident state (session-based) + delayed escalation scheduling
    session_id = payload.session_id or final_state.get("timestamp") or "session"
    decision = final_state.get("orchestrator_decision", {})
    safety_index = final_state.get("safety_index", {})
    decision2 = incident_manager.update_from_analysis(
        session_id=session_id,
        user_id=payload.user_id,
        payload=payload.model_dump(),
        decision=decision,
        safety_index=safety_index,
    )
    # Overwrite decision for response + action layer
    final_state["orchestrator_decision"] = decision2
    # Broadcast snapshot over WS
    snap = incident_manager.snapshot(session_id)
    if snap:
        await ws_manager.broadcast(session_id, {"type": "incident", "data": snap})
    await ws_manager.broadcast(session_id, {"type": "analysis", "data": {
        "safety_index": safety_index,
        "decision": decision2,
        "timestamp": final_state.get("timestamp"),
    }})
    
    return {
        "status": final_state.get("status", "error"),
        "layer1_monitoring": final_state.get("layer1_monitoring", final_state.get("safety_index")),
        "layer2_agents": final_state.get("layer2_agents", final_state.get("orchestrator_decision")),
        "layer3_actions": final_state.get("layer3_actions", final_state.get("action_results")),
        "timestamp": final_state.get("timestamp"),
        "session_id": session_id,
    }

@app.post("/api/routes")
async def get_routes(payload: RouteRequest):
    """
    Returns top 3 safest routes.
    Accepts optional safety_context (XGBoost ml_risk + crime_risk)
    to produce XGBoost-informed route risk weights.
    """
    start = {"lat": payload.start.lat, "lon": payload.start.lon}
    dest = {"lat": payload.destination.lat, "lon": payload.destination.lon}
    safety_context = payload.safety_context  # May be None

    routes = get_multiple_routes(start, dest, safety_context=safety_context)
    return {"routes": routes}

@app.post("/api/simulate")
async def simulate(payload: SimulationRequest):
    """
    Runs a deterministic simulation (recommended env):
      - NETRIKAN_AGENT_MODE=sim
      - NETRIKAN_NO_NETWORK=1

    Returns a per-step trace of Layer1 -> Layer2 -> Layer3.
    """
    if payload.steps is None:
        if not payload.scenario_id:
            raise HTTPException(status_code=400, detail="Provide scenario_id or steps[]")
        try:
            steps = [AnalyzeRequest(**s) for s in get_scenario_steps(payload.scenario_id)]
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
    else:
        steps = [AnalyzeRequest(**s) for s in payload.steps]

    results = []
    for step in steps:
        initial_state = {"payload": step.model_dump(), "status": "started"}
        final_state = await safety_app.ainvoke(initial_state)
        results.append(
            {
                "status": final_state.get("status", "error"),
                "layer1_processed": final_state.get("processed_data", {}),
                "layer1_monitoring": final_state.get("safety_index", {}),
                "layer2_agents": final_state.get("orchestrator_decision", {}),
                "layer3_actions": final_state.get("action_results", {}),
                "timestamp": final_state.get("timestamp"),
            }
        )

    return {"scenario_id": payload.scenario_id, "results": results}

@app.get("/api/simulate/scenarios")
def simulate_scenarios():
    return {"scenarios": list_scenarios()}


@app.post("/api/ack")
async def ack(payload: dict):
    session_id = str(payload.get("session_id") or "").strip()
    if not session_id:
        raise HTTPException(status_code=400, detail="session_id is required")
    ok = incident_manager.ack(session_id)
    if not ok:
        raise HTTPException(status_code=404, detail="incident not found")
    snap = incident_manager.snapshot(session_id)
    if snap:
        await ws_manager.broadcast(session_id, {"type": "incident", "data": snap})
    return {"status": "acknowledged", "session_id": session_id}


@app.websocket("/ws/incidents/{session_id}")
async def ws_incidents(websocket: WebSocket, session_id: str):
    await ws_manager.connect(session_id, websocket)
    try:
        snap = incident_manager.snapshot(session_id)
        if snap:
            await websocket.send_json({"type": "incident", "data": snap})
        while True:
            # Keep-alive; client may send pings or ignore
            await websocket.receive_text()
    except WebSocketDisconnect:
        await ws_manager.disconnect(session_id, websocket)
    except Exception:
        await ws_manager.disconnect(session_id, websocket)
        raise


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=settings.HOST, port=settings.PORT, reload=settings.RELOAD)
