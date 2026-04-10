from typing import Annotated, Dict, Any, List, TypedDict
from langgraph.graph import StateGraph, END
from core.layer1_monitoring import Layer1Monitoring
from core.layer2_agents import CommunicationOrchestrator
from core.layer3_actions import Layer3ActionExecutor
from core.policy import apply_action_policy
from utils.logger import get_logger

logger = get_logger("Orchestrator")

# Define the shared state for the 3-layer architecture
class SafetyState(TypedDict):
    # Input data from the user
    payload: Dict[str, Any]
    
    # Layer 1 outputs
    processed_data: Dict[str, Any]
    safety_index: Dict[str, Any]
    
    # Layer 2 outputs
    orchestrator_decision: Dict[str, Any]
    
    # Layer 3 outputs
    action_results: Dict[str, Any]
    
    # Metadata
    status: str
    timestamp: str

# Initialize the component instances
layer1 = Layer1Monitoring()
layer2 = CommunicationOrchestrator()
layer3 = Layer3ActionExecutor()

# --- Node Definitions ---

def monitoring_node(state: SafetyState) -> Dict[str, Any]:
    """Layer 1: Monitoring & Data Preprocessing"""
    logger.info("Node: Monitoring")
    payload = state["payload"]
    
    processed_data = layer1.preprocess(payload)
    safety_index = layer1.get_safety_index(processed_data)
    
    return {
        "processed_data": processed_data,
        "safety_index": safety_index,
        "timestamp": processed_data.get("timestamp", "")
    }

def reasoning_node(state: SafetyState) -> Dict[str, Any]:
    """Layer 2: AI Decision & Reasoning Agents"""
    logger.info("Node: Reasoning")
    processed_data = state["processed_data"]
    safety_index = state["safety_index"]
    
    decision_raw = layer2.orchestrate(processed_data, safety_index)
    decision = apply_action_policy(decision_raw, processed_data, safety_index)
    
    return {
        "orchestrator_decision": decision
    }

def action_node(state: SafetyState) -> Dict[str, Any]:
    """Layer 3: Action & Communication"""
    logger.info("Node: Action")
    decision = state["orchestrator_decision"]
    processed_data = state["processed_data"]
    
    results = layer3.execute_actions(decision, processed_data)
    
    return {
        "action_results": results,
        "status": "success"
    }

# --- Graph Construction ---

def create_safety_graph():
    # Initialize the graph with our state schema
    workflow = StateGraph(SafetyState)

    # 1. Add nodes (one for each layer)
    workflow.add_node("monitoring", monitoring_node)
    workflow.add_node("reasoning", reasoning_node)
    workflow.add_node("action", action_node)

    # 2. Define the flow (linear as per current logic, can be conditional later)
    workflow.set_entry_point("monitoring")
    workflow.add_edge("monitoring", "reasoning")
    workflow.add_edge("reasoning", "action")
    workflow.add_edge("action", END)

    # Compile the graph
    return workflow.compile()

# Singleton graph app
safety_app = create_safety_graph()
