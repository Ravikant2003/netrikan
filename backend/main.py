from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.concurrency import run_in_threadpool
from fastapi.middleware.cors import CORSMiddleware
from config import settings
from utils.logger import get_logger
from core.orchestrator import safety_app
from schemas import AnalyzeRequest, AnalyzeResponse, RouteRequest, SimulationRequest, PushTokenRegisterRequest
from utils.maps_api import get_multiple_routes
from simulation.scenarios import get_scenario_steps, list_scenarios
from services.incidents import incident_manager
from services.ws_manager import ws_manager
from services.push_tokens import register_token
from services.notifiers import get_notifier


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


@app.get("/api/webhooks/status")
def webhook_status():
    """Check webhook configuration status."""
    try:
        from services.webhook_handler import get_webhook_handler
        handler = get_webhook_handler()
        return {
            "status": "ok",
            "configured": handler.is_configured(),
            "endpoints": {
                "push": bool(handler.push_url),
                "sms": bool(handler.sms_url),
                "call": bool(handler.call_url),
                "police": bool(handler.police_url)
            }
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}


@app.post("/api/webhooks/test")
def test_webhook():
    """Test webhook by sending a test payload."""
    try:
        from services.webhook_handler import get_webhook_handler
        import asyncio
        handler = get_webhook_handler()
        
        if not handler.is_configured():
            return {"status": "not_configured", "message": "No webhooks configured. Set NETRIKAN_*_WEBHOOK_URL in .env"}
        
        # Test push webhook
        result = asyncio.run(handler.send_push("test_user", "Test Alert", "This is a test from Netrikan", {"test": True}))
        
        return {"status": "ok", "test_result": result}
    except Exception as e:
        return {"status": "error", "error": str(e)}


@app.get("/api/actions/queue")
def get_queue_status():
    """Get action queue status."""
    try:
        from services.action_queue import get_queue_stats
        return {"status": "ok", "queue": get_queue_stats()}
    except Exception as e:
        return {"status": "error", "error": str(e)}


@app.post("/api/actions/process")
def process_actions(max_actions: int = 10):
    """Manually trigger processing of pending actions."""
    try:
        from services.action_processor import process_pending_actions
        result = process_pending_actions(max_actions=max_actions)
        return {"status": "ok", "result": result}
    except Exception as e:
        return {"status": "error", "error": str(e)}

@app.post("/api/analyze")
async def analyze(payload: AnalyzeRequest):
    """
    Analysis endpoint - executes Layer 1 (Monitoring) and Layer 2 (Reasoning) only.
    Layer 3 (Actions) is skipped - user must confirm first via /api/analyze/confirm
    This implements Human-in-the-Loop for ALL alerts.
    """
    logger.info("New analysis request received via LangGraph")
    
    from core.orchestrator import layer1, layer2
    from core.policy import apply_action_policy
    
    # Run only Layer 1 (Monitoring)
    processed_data = await run_in_threadpool(layer1.preprocess, payload.model_dump())
    safety_index = await run_in_threadpool(layer1.get_safety_index, processed_data)
    
    # Run only Layer 2 (Reasoning)
    decision = await run_in_threadpool(layer2.orchestrate, processed_data, safety_index)
    decision = await run_in_threadpool(apply_action_policy, decision, processed_data, safety_index)
    
    # Store data for later use in confirm endpoint (medium only)
    session_id = payload.session_id or f"session_{payload.user_id}"
    decision_type = decision.get("decision", "NORMAL_MONITORING")
    if decision_type == "ROUTE_ADJUSTMENT":
        if not hasattr(analyze, '_pending_actions'):
            analyze._pending_actions = {}
        analyze._pending_actions[session_id] = {
            'decision': decision,
            'data': payload.model_dump(),
        }
    
    # Return result without executing Layer 3
    final_state = {
        "status": "success",
        "layer1_monitoring": safety_index,
        "layer2_agents": decision,
        "layer3_actions": {},
        "timestamp": "",
    }
    
    # HITL required for MEDIUM, auto-trigger for HIGH
    risk_class = "none"
    if decision_type == "EMERGENCY_ESCALATION":
        risk_class = "high"
    elif decision_type == "ROUTE_ADJUSTMENT":
        risk_class = "medium"
    elif decision_type == "INCREASED_MONITORING":
        risk_class = "low"

    hitl_required = (risk_class == "medium")
    
    # Auto-execute Layer 3 for HIGH risk if not HITL
    has_distress = bool(
        (decision.get("policy") or {})
        .get("signals", {})
        .get("has_distress_text")
    )
    severity = str(processed_data.get("severity", "")).lower()
    allow_auto_send = decision_type == "EMERGENCY_ESCALATION" and (has_distress or severity == "high")

    layer3_actions = {}
    if allow_auto_send or decision_type == "ROUTE_ADJUSTMENT":
        from core.orchestrator import layer3
        layer3_actions = await run_in_threadpool(layer3.execute_actions, decision, payload.model_dump())
        logger.info(f"Layer 3 executed - Decision: {decision_type}, Actions: {list(layer3_actions.keys())}")
    
    return {
        "status": final_state.get("status", "success"),
        "layer1_monitoring": safety_index,
        "layer2_agents": decision,
        "layer3_actions": layer3_actions,
        "timestamp": final_state.get("timestamp", ""),
        "session_id": session_id,
        "hitl_required": hitl_required,
        "risk_class": risk_class,
    }

@app.post("/api/analyze/confirm")
async def confirm_action(payload: dict):
    """
    Human-in-the-Loop endpoint for MEDIUM severity confirmation.
    User confirms or cancels the pending action.
    """
    session_id = payload.get("session_id", "")
    user_id = payload.get("user_id", "")
    confirmed = payload.get("confirmed", False)
    data = payload.get("data", {})
    
    logger.info(f"HITL confirmation: session={session_id}, user={user_id}, confirmed={confirmed}, data={data}")
    
    if confirmed:
        # Get stored pending actions
        pending = getattr(analyze, '_pending_actions', {}).get(session_id)
        
        if pending:
            decision = pending.get('decision', {})
            data = pending.get('data', {})
            
            # Execute Layer 3 with the stored decision
            from core.orchestrator import layer3
            results = await run_in_threadpool(layer3.execute_actions, decision, data)
            
            logger.info(f"HITL confirmed - Actions executed: {list(results.keys())}")
            
            # Clear the pending action
            if hasattr(analyze, '_pending_actions'):
                analyze._pending_actions.pop(session_id, None)
            
            return {"status": "ok", "actions_triggered": results, "message": "Emergency alerts sent!"}
        else:
            return {"status": "already_processed", "message": "No pending action for this session."}
    else:
        # Clear pending action
        if hasattr(analyze, '_pending_actions'):
            analyze._pending_actions.pop(session_id, None)
        logger.info(f"HITL cancelled by user")
        return {"status": "cancelled", "message": "Alert cancelled by user"}

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

    if payload.user_id:
        for step in steps:
            if not step.user_id:
                step.user_id = payload.user_id

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


@app.post("/api/push/register")
def register_push_token(payload: PushTokenRegisterRequest):
    user_id = payload.user_id.strip()
    token = payload.token.strip()
    if not user_id or not token:
        raise HTTPException(status_code=400, detail="user_id and token are required")
    count = register_token(user_id, token)
    logger.info(f"Registered push token for user_id={user_id}. token_count={count}")
    return {"status": "ok", "user_id": user_id, "tokens": count}


@app.post("/api/push/test")
async def test_push(payload: dict):
    user_id = str(payload.get("user_id") or "").strip()
    title = str(payload.get("title") or "Netrikan Test")
    body = str(payload.get("body") or "Test push from Netrikan backend.")
    if not user_id:
        raise HTTPException(status_code=400, detail="user_id is required")
    notifier = get_notifier()
    await notifier.send_push(user_id, title, body, data={"source": "push_test"})
    return {"status": "sent", "user_id": user_id}


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
    # Start background action processor
    try:
        from services.action_processor import start_background_processor
        start_background_processor(interval_seconds=5, max_actions=10)
        logger.info("Background action processor started")
    except Exception as e:
        logger.warning(f"Could not start background processor: {e}")
    
    import uvicorn
    uvicorn.run("main:app", host=settings.HOST, port=settings.PORT, reload=settings.RELOAD)
