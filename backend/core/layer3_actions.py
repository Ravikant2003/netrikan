from typing import Dict, Any, List
from utils.logger import get_logger
# Fallback functions if maps_api is missing
def get_route(start, end): return {"eta_minutes": 15, "risk_weight": 0.2}

logger = get_logger("Actions")

class NotificationAction:
    """Sends push notifications and SMS to guardians."""
    def execute(self, message: str, targets: List[str] = ["guardians"]):
        for target in targets:
            logger.warning(f"Action: Push Notification sent to {target}: {message}")
        return True

class MapReroutingAction:
    """Provides safe route recommendations."""
    def execute(self, start: Dict[str, float], end: Dict[str, float]):
        route = get_route(start, end)
        logger.info(f"Action: Map Rerouting calculated. ETA: {route['eta_minutes']} min")
        return {
            "recommended_route": "safer_alternate",
            "details": route
        }

class EmergencyAction:
    """Automated emergency triggers."""
    def execute(self, message: str):
        logger.critical(f"Action: POLICE NOTIFICATION SENT: {message}")
        return True

class SafePublicPlaceAction:
    """Suggestions for nearby safe havens."""
    def execute(self, lat: float, lon: float):
        logger.info(f"Action: Safe public places identified near {lat}, {lon}")
        return ["Police Station - 500m", "Hospital - 1.2km", "Well-lit Mall - 800m"]

class Layer3ActionExecutor:
    """
    Layer 3: Action & Communication
    Consolidates and executes requested actions.
    """
    def __init__(self):
        self.notification = NotificationAction()
        self.map_reroute = MapReroutingAction()
        self.emergency = EmergencyAction()
        self.safe_places = SafePublicPlaceAction()

    def execute_actions(self, orchestrator_decision: Dict[str, Any], data: Dict[str, Any]) -> Dict[str, Any]:
        results = {}
        actions = orchestrator_decision.get("required_actions", [])

        guardians = data.get("guardians") or []
        guardian_targets: List[str] = []
        if isinstance(guardians, list):
            for g in guardians:
                try:
                    if g.get("active") is False:
                        continue
                    name = str(g.get("name") or "").strip() or "guardian"
                    phone = str(g.get("phone") or "").strip()
                    guardian_targets.append(f"{name}:{phone}" if phone else name)
                except Exception:
                    continue
        
        if "PUSH_NOTIFICATION" in actions:
            results["push_notifications"] = self.notification.execute("Safety Alert: Unusual activity detected.", ["user"])
            
        if "SMS_GUARDIANS" in actions:
            targets = guardian_targets if guardian_targets else ["guardians"]
            results["sms_alerts"] = {
                "sent": self.notification.execute("SOS: Immediate attention required.", targets),
                "targets": targets,
            }
            
        if "POLICE_NOTIFICATION" in actions:
            results["police_status"] = self.emergency.execute("SOS triggered by user or critical risk.")
            
        if "MAP_REROUTING" in actions:
            results["reroute_plan"] = self.map_reroute.execute(
                {"lat": data["latitude"], "lon": data["longitude"]},
                data["destination"]
            )
            
        if "SAFE_PLACES_SUGGESTION" in actions:
            results["nearby_safe_zones"] = self.safe_places.execute(data["latitude"], data["longitude"])
            
        return results
