import os
import json
import re
from typing import Dict, Any, List

from dotenv import load_dotenv
from utils.logger import get_logger

load_dotenv()

logger = get_logger("Layer2Agents")

# Groq LLM for Layer 2 AI agents
api_key = os.environ.get("GROQ_API_KEY")

model_name = os.environ.get("NETRIKAN_LLM_MODEL", "llama-3.1-8b-instant").strip() or "llama-3.1-8b-instant"
try:
    max_tokens = int(os.environ.get("NETRIKAN_LLM_MAX_TOKENS", "128"))
except Exception:
    max_tokens = 128

if not api_key:
    raise ValueError(
        "GROQ_API_KEY is not set. Add it to backend/.env (recommended) or export it in your shell."
    )

# Fix for langchain-core 0.2.x compatibility
import langchain
if not hasattr(langchain, "verbose"):
    langchain.verbose = False
if not hasattr(langchain, "debug"):
    langchain.debug = False
if not hasattr(langchain, "llm_cache"):
    langchain.llm_cache = None

from langchain_core.tools import tool
from langchain_groq import ChatGroq

llm = ChatGroq(
    model=model_name,
    groq_api_key=api_key,
    temperature=0.2,
    max_tokens=max_tokens,
)


def _safe_json_load(raw: str) -> Dict[str, Any]:
    try:
        parsed = json.loads(raw)
        if isinstance(parsed, dict):
            return parsed
    except Exception:
        pass
    return {}


def _extract_json(text: str) -> Dict[str, Any]:
    """Extract JSON from any text response."""
    try:
        return json.loads(text)
    except:
        pass
    
    try:
        match = re.search(r'\{[^{}]*\}', text, re.DOTALL)
        if match:
            return json.loads(match.group())
    except:
        pass
    
    try:
        start = text.find('{')
        end = text.rfind('}')
        if start >= 0 and end > start:
            return json.loads(text[start:end+1])
    except:
        pass
    
    return {}


def check_sos(text_signal: str) -> bool:
    """Simple SOS check."""
    text = str(text_signal).lower()
    return "help" in text or "emergency" in text or "sos" in text or "attack" in text or "danger" in text


# --- 1. Emergency Agent Tools ---
@tool
def evaluate_sos_threat(text_signal: str) -> str:
    """Evaluates if the provided text signal constitutes a critical emergency or SOS."""
    if check_sos(text_signal):
        return "CRITICAL_SOS_DETECTED"
    return "NO_SOS_DETECTED"


@tool
def escalate_emergency(reason: str) -> str:
    """Use this tool to formally trigger an emergency escalation."""
    return f"ESCALATION_TRIGGERED: {reason}"


# --- 2. Route Rationalization Agent Tools ---
@tool
def check_route_deviations(deviation: bool, risk_score: float) -> str:
    """Analyzes if a route deviation combined with risk score warrants reroute."""
    if deviation or risk_score > 0.6:
        return "REROUTE_RECOMMENDED"
    return "ROUTE_SAFE"


# --- 3. Personal Safety Agent Tools ---
@tool
def analyze_behavior(speed: str) -> str:
    """Analyzes user movement behavior for anomalies."""
    try:
        spd = float(speed)
        if spd > 80:
            return "HIGH_RISK_BEHAVIOR"
    except:
        pass
    return "NORMAL_BEHAVIOR"


class EmergencyAgent:
    def __init__(self):
        self.llm = llm
    
    def _fallback_analyze(self, data: Dict, safety_index: Dict) -> Dict:
        emergency_data = safety_index.get("emergency_anomaly", {})
        text_signal = str(data.get("text_signal", "")).lower()
        level = str(emergency_data.get("level", "NONE")).upper()
        sos = check_sos(text_signal)
        return {
            "sos_detected": sos or level == "CRITICAL",
            "escalation_required": sos or level == "CRITICAL",
            "confidence": 0.5,
            "reasoning": "Rule-based fallback",
            "factors_considered": ["sos_keywords", "emergency_level"],
        }

    def analyze(self, data: Dict, safety_index: Dict) -> Dict:
        text_signal = str(data.get("text_signal", ""))
        emergency_data = safety_index.get("emergency_anomaly", {}) or {}
        level = str(emergency_data.get("level", "NONE")).upper()
        risk_score = float(safety_index.get("risk_score", 0) or 0)
        is_alone = bool(data.get("is_user_alone", True))
        
        prompt = f"""You are a safety expert. Analyze if emergency escalation is needed.

Current situation:
- Text signal: "{text_signal}"
- Emergency level: {level}
- Risk score: {risk_score}
- User alone: {is_alone}

Respond ONLY with JSON:
{{"reasoning": "1 sentence analysis", "decision": "ESCALATE or NO_ESCALATE", "confidence": 0.0-1.0}}}}"""

        logger.info("🤖 [Emergency Agent] Invoking Groq LLM (llama-3.1-8b-instant)...")
        
        try:
            response = self.llm.invoke(prompt)
            response_text = str(response.content) if hasattr(response, 'content') else str(response)
            
            logger.info("📨 [Emergency Agent] LLM Response received")
            
            parsed = _extract_json(response_text)
            if parsed:
                decision = parsed.get("decision", "NO_ESCALATE")
                confidence = float(parsed.get("confidence", 0.5))
                return {
                    "sos_detected": check_sos(text_signal) or level == "CRITICAL",
                    "escalation_required": decision.upper() == "ESCALATE" or confidence > 0.7,
                    "confidence": confidence,
                    "reasoning": parsed.get("reasoning", "LLM analysis"),
                    "factors_considered": ["llm_analysis", "sos_check", "risk_score"],
                }
        except Exception as e:
            logger.warning(f"EmergencyAgent LLM error: {e}")
        
        return self._fallback_analyze(data, safety_index)


class RouteRationalizationAgent:
    def __init__(self):
        self.llm = llm
    
    def _fallback_analyze(self, data: Dict, safety_index: Dict) -> Dict:
        deviation = bool(data.get("route_deviation", False))
        route_risk = float(safety_index.get("route_risk", 0) or 0)
        risk_score = float(safety_index.get("risk_score", 0) or 0)
        return {
            "unsafe_zone_detected": route_risk > 0.5,
            "route_deviation_detected": deviation,
            "reroute_recommended": deviation or route_risk > 0.5 or risk_score > 0.6,
            "confidence": 0.5,
            "reasoning": "Rule-based fallback",
        }

    def analyze(self, data: Dict, safety_index: Dict) -> Dict:
        deviation = bool(data.get("route_deviation", False))
        route_risk = float(safety_index.get("route_risk", 0) or 0)
        risk_score = float(safety_index.get("risk_score", 0) or 0)
        
        prompt = f"""You are a route safety expert. Analyze if rerouting is needed.

- Route deviation: {deviation}
- Route risk: {route_risk}
- Risk score: {risk_score}

Respond ONLY with JSON:
{{"reasoning": "1 sentence", "decision": "REROUTE or KEEP_ROUTE", "confidence": 0.0-1.0}}}}"""

        logger.info("🤖 [Route Agent] Invoking Groq LLM (llama-3.1-8b-instant)...")
        
        try:
            response = self.llm.invoke(prompt)
            response_text = str(response.content) if hasattr(response, 'content') else str(response)
            
            logger.info("📨 [Route Agent] LLM Response received")
            
            parsed = _extract_json(response_text)
            if parsed:
                decision = parsed.get("decision", "KEEP_ROUTE")
                confidence = float(parsed.get("confidence", 0.5))
                return {
                    "unsafe_zone_detected": route_risk > 0.5,
                    "route_deviation_detected": deviation,
                    "reroute_recommended": decision.upper() == "REROUTE" or confidence > 0.6,
                    "confidence": confidence,
                    "reasoning": parsed.get("reasoning", "LLM analysis"),
                }
        except Exception as e:
            logger.warning(f"RouteAgent LLM error: {e}")
        
        return self._fallback_analyze(data, safety_index)


class PersonalSafetyAgent:
    def __init__(self):
        self.llm = llm
    
    def _fallback_analyze(self, data: Dict, safety_index: Dict) -> Dict:
        speed = float(data.get("speed", 0) or 0)
        crime_score = float(safety_index.get("crime_score", 0) or 0)
        return {
            "behavioral_anomaly": speed > 80 or crime_score > 0.7,
            "personal_risk_level": "HIGH" if speed > 80 or crime_score > 0.7 else "LOW",
            "confidence": 0.5,
            "reasoning": "Rule-based fallback",
        }

    def analyze(self, data: Dict, safety_index: Dict) -> Dict:
        speed = float(data.get("speed", 0) or 0)
        crime_score = float(safety_index.get("crime_score", 0) or 0)
        
        prompt = f"""You are a personal safety expert. Analyze behavior.

- Speed: {speed} km/h
- Crime score: {crime_score}

Respond ONLY with JSON:
{{"reasoning": "1 sentence", "decision": "HIGH_RISK or NORMAL", "confidence": 0.0-1.0}}}}"""

        logger.info("🤖 [Personal Agent] Invoking Groq LLM (llama-3.1-8b-instant)...")
        
        try:
            response = self.llm.invoke(prompt)
            response_text = str(response.content) if hasattr(response, 'content') else str(response)
            
            logger.info("📨 [Personal Agent] LLM Response received")
            
            parsed = _extract_json(response_text)
            if parsed:
                decision = parsed.get("decision", "NORMAL")
                confidence = float(parsed.get("confidence", 0.5))
                return {
                    "behavioral_anomaly": decision.upper() == "HIGH_RISK" or confidence > 0.7,
                    "personal_risk_level": decision.upper(),
                    "confidence": confidence,
                    "reasoning": parsed.get("reasoning", "LLM analysis"),
                }
        except Exception as e:
            logger.warning(f"PersonalSafetyAgent LLM error: {e}")
        
        return self._fallback_analyze(data, safety_index)


class CommunicationOrchestrator:
    def __init__(self):
        self.emergency_agent = EmergencyAgent()
        self.route_agent = RouteRationalizationAgent()
        self.safety_agent = PersonalSafetyAgent()

    def orchestrate(self, data: Dict[str, Any], safety_index: Dict[str, Any]) -> Dict[str, Any]:
        ml_risk = float(safety_index.get("risk_score", 0) or 0)
        crime_risk = float(safety_index.get("crime_score", 0) or 0)
        route_risk = float(safety_index.get("route_risk", 0) or 0)
        
        weighted_risk = (0.55 * ml_risk) + (0.25 * crime_risk) + (0.20 * route_risk)
        
        # Boosters
        emergency_data = safety_index.get("emergency_anomaly", {})
        if emergency_data.get("level") == "CRITICAL":
            weighted_risk = min(1.0, weighted_risk + 0.25)
        elif emergency_data.get("level") == "ELEVATED":
            weighted_risk = min(1.0, weighted_risk + 0.10)
        
        # Get agent insights - Each calls Groq LLM
        logger.info("🔄 [Orchestrator] Starting Layer 2 - Calling AI Agents...")
        
        logger.info("📡 [Orchestrator] Invoking Emergency Agent (Groq LLM)...")
        emergency_status = self.emergency_agent.analyze(data, safety_index)
        logger.info(f"✅ [Emergency Agent] Result: sos_detected={emergency_status.get('sos_detected')}, escalation={emergency_status.get('escalation_required')}")
        
        logger.info("📡 [Orchestrator] Invoking Route Agent (Groq LLM)...")
        route_status = self.route_agent.analyze(data, safety_index)
        logger.info(f"✅ [Route Agent] Result: reroute={route_status.get('reroute_recommended')}, unsafe_zone={route_status.get('unsafe_zone_detected')}")
        
        logger.info("📡 [Orchestrator] Invoking Personal Agent (Groq LLM)...")
        personal_status = self.safety_agent.analyze(data, safety_index)
        logger.info(f"✅ [Personal Agent] Result: anomaly={personal_status.get('behavioral_anomaly')}, risk_level={personal_status.get('personal_risk_level')}")
        
        # Calculate confidence
        confidences = [emergency_status.get("confidence", 0.5), 
                       route_status.get("confidence", 0.5),
                       personal_status.get("confidence", 0.5)]
        ensemble_confidence = sum(confidences) / len(confidences)
        
        # Decision logic with three notification levels
        sos_detected = emergency_status.get("sos_detected", False)
        
        # HIGH severity - Automatic notifications (Telegram + Phone + Email)
        # Trigger only if: SOS detected OR emergency escalation required AND high risk
        if sos_detected or (emergency_status.get("escalation_required") and weighted_risk > 0.7):
            decision = "EMERGENCY_ESCALATION"
            actions = ["TELEGRAM_NOTIFY", "ADB_CALL", "POLICE_NOTIFICATION", "PUSH_NOTIFICATION", "SMS_GUARDIANS", "EMAIL_GUARDIANS"]
        # MEDIUM severity - Human in the loop (Telegram only, requires human confirmation)
        # Trigger if: route reroute recommended AND medium risk (lowered threshold)
        elif route_status.get("reroute_recommended") and weighted_risk > 0.4:
            decision = "ROUTE_ADJUSTMENT"
            actions = ["TELEGRAM_NOTIFY", "SAFE_PLACES_SUGGESTION", "PUSH_NOTIFICATION"]
        # LOW severity - Log only, no alert
        # Trigger if: behavioral anomaly detected AND low-medium risk
        elif personal_status.get("behavioral_anomaly") and weighted_risk > 0.35:
            decision = "INCREASED_MONITORING"
            actions = ["SAFE_PLACES_SUGGESTION"]
        else:
            decision = "NORMAL_MONITORING"
            actions = []
        
        return {
            "decision": decision,
            "weighted_risk_score": round(weighted_risk, 4),
            "ensemble_confidence": round(ensemble_confidence, 3),
            "required_actions": actions,
            "agent_insights": {
                "emergency": emergency_status,
                "route": route_status,
                "personal": personal_status
            }
        }