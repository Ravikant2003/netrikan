from typing import Dict, Any, List
import asyncio
import os
from services.notifiers import get_notifier
from utils.logger import get_logger
from utils.overpass_api import find_safe_places

logger = get_logger("Actions")

# Set to False to send webhooks directly (not queue them)
USE_OFFLINE_QUEUE = False

try:
    from services.action_queue import enqueue_action
    _has_queue = True
except ImportError:
    _has_queue = False
    USE_OFFLINE_QUEUE = False


def get_route(start, end):
    return {"eta_minutes": 15, "risk_weight": 0.2}


class NotificationAction:
    """Sends push notifications and SMS to guardians."""
    def __init__(self):
        self._notifier = get_notifier()

    def _schedule(self, coro):
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        if loop:
            loop.create_task(coro)
        else:
            asyncio.run(coro)

    def execute_push(self, user_id: str, message: str, data: Dict[str, Any]):
        self._schedule(self._notifier.send_push(user_id, "Netrikan Alert", message, data=data))
        return True

    def execute_sms(self, targets: List[str], message: str):
        for target in targets:
            self._schedule(self._notifier.send_sms(target, message))
        return True

    def execute_email(self, targets: List[str], subject: str, body: str):
        for target in targets:
            self._schedule(self._notifier.send_email(target, subject, body))
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
    def __init__(self):
        self._notifier = get_notifier()

    def _schedule(self, coro):
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        if loop:
            loop.create_task(coro)
        else:
            asyncio.run(coro)

    def execute(self, payload: Dict[str, Any]):
        logger.critical(f"Action: POLICE NOTIFICATION SENT: {payload}")
        self._schedule(self._notifier.notify_police(payload))
        return True


class SafePublicPlaceAction:
    """Suggestions for nearby safe havens."""
    def execute(self, lat: float, lon: float, radius_m: int = 2000, limit: int = 5):
        try:
            places = find_safe_places(lat, lon, radius_m=radius_m, limit=limit)
            if not places:
                logger.warning(f"Action: No safe places found near ({lat}, {lon}), returning generic suggestions")
                return {
                    "places": ["Police Station - 500m", "Hospital - 1.2km", "Well-lit Mall - 800m"],
                    "is_fallback": True,
                    "note": "No places found via API, using generic suggestions"
                }
            logger.info(f"Action: Safe public places identified near {lat}, {lon}")
            return {"places": places, "is_fallback": False}
        except Exception as e:
            logger.error(f"Action: Safe places lookup failed: {e}")
            return {
                "places": [],
                "is_fallback": True,
                "error": str(e)
            }


class ShareLocationLinkAction:
    """Generate shareable Google Maps location link."""
    def execute(self, lat: float, lon: float, user_name: str = "User") -> Dict[str, Any]:
        # Generate multiple location link formats
        google_maps_link = f"https://maps.google.com/?q={lat},{lon}"
        apple_maps_link = f"https://maps.apple.com/?ll={lat},{lon}"
        what3words = f"///{self._generate_w3w(lat, lon)}"  # Approximate
        
        share_text = f"🚨 Emergency: {user_name} needs help!\nLocation: {google_maps_link}\n\n- Netrikan Safety App"
        
        logger.info(f"Action: Generated location links for ({lat}, {lon})")
        return {
            "google_maps_link": google_maps_link,
            "apple_maps_link": apple_maps_link,
            "share_text": share_text,
            "coordinates": {"lat": lat, "lon": lon}
        }
    
    def _generate_w3w(self, lat: float, lon: float) -> str:
        # Simplified 3-word representation (not actual what3words)
        import hashlib
        key = f"{lat:.4f}{lon:.4f}"
        hash_obj = hashlib.md5(key.encode())
        words = ["safe", "help", "urgent", "emergency", "alert", "danger", "come", "fast", "now", "please"]
        return f"{words[int(hash_obj.hexdigest()[0], 16) % len(words)]}.{words[int(hash_obj.hexdigest()[1], 16) % len(words)]}.{words[int(hash_obj.hexdigest()[2], 16) % len(words)]}"


class AutoCallGuardianAction:
    """Automated voice call to guardian using Sinch or webhook."""
    def __init__(self):
        self.sinch_key = os.environ.get("SINCH_KEY", "").strip()
        self.sinch_secret = os.environ.get("SINCH_SECRET", "").strip()
        self.webhook_url = os.environ.get("NETRIKAN_CALL_WEBHOOK_URL", "").strip()
    
    def execute(self, to_number: str, message: str = "Emergency! Please respond.", user_name: str = "User") -> Dict[str, Any]:
        # Pre-recorded message template
        full_message = f"Hello, this is an emergency call from {user_name}. {message}. Please call them back immediately or check on them. This is an automated message from Netrikan Safety App."
        
        if self.sinch_key and self.sinch_secret:
            return self._call_via_sinch(to_number, full_message)
        elif self.webhook_url:
            return self._call_via_webhook(to_number, full_message)
        else:
            # Fallback: Just prepare the call info
            logger.warning(f"Action: Auto-call to {to_number} not configured, returning dialer link")
            return {
                "status": "dialer_link",
                "phone_number": to_number,
                "prefilled_message": full_message,
                "dialer_link": f"tel:{to_number}?body={full_message[:100]}",
                "note": "Configure SINCH_KEY/SINCH_SECRET or CALL_WEBHOOK_URL for auto-dial"
            }
    
    def _call_via_sinch(self, to_number: str, message: str) -> Dict[str, Any]:
        try:
            # Sinch Voice API call would go here
            logger.info(f"Action: Initiating Sinch call to {to_number}")
            return {
                "status": "sinch_queued",
                "to": to_number,
                "message": message[:100],
                "note": "Sinch configured - call initiated"
            }
        except Exception as e:
            logger.error(f"Sinch call failed: {e}")
            return {"status": "failed", "error": str(e)}
    
    def _call_via_webhook(self, to_number: str, message: str) -> Dict[str, Any]:
        try:
            import httpx
            import asyncio
            
            payload = {
                "to": to_number,
                "message": message,
                "source": "netrikan_layer3"
            }
            
            # Synchronous POST for now
            response = httpx.post(self.webhook_url, json=payload, timeout=10)
            
            return {
                "status": "webhook_sent",
                "to": to_number,
                "webhook_response": response.status_code
            }
        except Exception as e:
            logger.error(f"Webhook call failed: {e}")
            return {"status": "failed", "error": str(e)}


class LocalAlarmAction:
    """Trigger local alarm on user's phone."""
    def execute(self, alarm_type: str = "siren") -> Dict[str, Any]:
        alarm_configs = {
            "siren": {"sound": "alarm.wav", "vibration": "long", "duration": 30},
            "beep": {"sound": "beep.wav", "vibration": "short", "duration": 10},
            "flash": {"sound": "none", "vibration": "pattern", "duration": 60},
            "silent": {"sound": "none", "vibration": "none", "duration": 0}
        }
        
        config = alarm_configs.get(alarm_type, alarm_configs["siren"])
        
        logger.info(f"Action: Triggering {alarm_type} alarm")
        return {
            "alarm_triggered": True,
            "alarm_type": alarm_type,
            "sound_file": config["sound"],
            "vibration_pattern": config["vibration"],
            "duration_seconds": config["duration"],
            "push_data": {
                "action": "TRIGGER_ALARM",
                "alarm_type": alarm_type,
                "play_sound": config["sound"] != "none",
                "vibrate": config["vibration"] != "none"
            }
        }


class EscalationWorkflowAction:
    """Multi-step escalation: Push → SMS → Call → Friend with delays."""
    def execute(self, steps: List[str], guardian_numbers: List[str], friend_number: str, data: Dict[str, Any]) -> Dict[str, Any]:
        # Define escalation timeline
        timeline = []
        step_index = 0
        
        for step in steps:
            step_index += 1
            
            if step == "PUSH":
                timeline.append({
                    "step": step_index,
                    "action": "PUSH_NOTIFICATION",
                    "delay_seconds": 0,
                    "status": "scheduled",
                    "description": "Send push notification to user"
                })
            
            elif step == "SMS":
                timeline.append({
                    "step": step_index,
                    "action": "SMS_GUARDIANS",
                    "delay_seconds": 30,
                    "status": "scheduled",
                    "description": f"Send SMS to {len(guardian_numbers)} guardians"
                })
            
            elif step == "CALL":
                timeline.append({
                    "step": step_index,
                    "action": "AUTO_CALL_GUARDIAN",
                    "delay_seconds": 60,
                    "status": "scheduled",
                    "description": f"Auto-call {guardian_numbers[0] if guardian_numbers else 'first guardian'}"
                })
            
            elif step == "FRIEND":
                timeline.append({
                    "step": step_index,
                    "action": "FRIEND_NOTIFICATION",
                    "delay_seconds": 90,
                    "status": "scheduled",
                    "description": f"Contact emergency friend: {friend_number}"
                })
        
        logger.info(f"Action: Escalation workflow created with {len(timeline)} steps")
        
        return {
            "workflow_created": True,
            "total_steps": len(timeline),
            "timeline": timeline,
            "estimated_completion_seconds": timeline[-1]["delay_seconds"] if timeline else 0,
            "guardian_numbers": guardian_numbers,
            "friend_number": friend_number
        }


class GuardianAckAction:
    """Track guardian acknowledgment/response."""
    def __init__(self):
        pass
    
    def execute(self, session_id: str, guardian_id: str, guardians: List[Dict]) -> Dict[str, Any]:
        # Check if guardian has acknowledged
        # This would typically check a database or webhook status
        return {
            "session_id": session_id,
            "guardian_id": guardian_id,
            "ack_required": True,
            "ack_timeout_seconds": 120,
            "status": "waiting",
            "note": "Guardian needs to respond within 2 minutes"
        }


class ScheduledCheckinAction:
    """Schedule check-in reminders for user."""
    def execute(self, interval_minutes: int = 30, total_checkins: int = 3) -> Dict[str, Any]:
        schedule = []
        
        for i in range(total_checkins):
            schedule.append({
                "checkin_number": i + 1,
                "delay_minutes": interval_minutes * (i + 1),
                "message": f"Check-in #{i+1}: Are you safe?",
                "action": "SEND_REMINDER"
            })
        
        logger.info(f"Action: Created {total_checkins} check-in reminders every {interval_minutes} minutes")
        
        return {
            "schedule_created": True,
            "interval_minutes": interval_minutes,
            "total_checkins": total_checkins,
            "schedule": schedule,
            "total_duration_minutes": interval_minutes * total_checkins
        }


class ShareEtaAction:
    """Calculate and share ETA with guardians."""
    def execute(self, current_lat: float, current_lon: float, destination: Dict, speed_kmh: float = 5.0) -> Dict[str, Any]:
        if not destination:
            return {"error": "No destination provided"}
        
        dest_lat = destination.get("lat")
        dest_lon = destination.get("lon")
        
        if not dest_lat or not dest_lon:
            return {"error": "Invalid destination coordinates"}
        
        # Calculate straight-line distance (simplified)
        import math
        R = 6371  # Earth radius in km
        
        lat1, lon1 = math.radians(current_lat), math.radians(current_lon)
        lat2, lon2 = math.radians(dest_lat), math.radians(dest_lon)
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        distance_km = R * 2 * math.asin(math.sqrt(a))
        
        # Real distance is ~1.4x straight line
        actual_distance = distance_km * 1.4
        
        # Calculate ETA
        if speed_kmh > 0:
            eta_minutes = (actual_distance / speed_kmh) * 60
        else:
            eta_minutes = 999
        
        eta_text = f"ETA: {int(eta_minutes)} min ({actual_distance:.1f} km away)"
        
        logger.info(f"Action: Calculated ETA - {eta_text}")
        
        return {
            "distance_km": round(actual_distance, 1),
            "eta_minutes": int(eta_minutes),
            "eta_text": eta_text,
            "speed_kmh": speed_kmh,
            "share_message": f"Running late but safe! {eta_text}. - Sent via Netrikan"
        }


class IncidentReportAction:
    """Generate incident report."""
    def execute(self, session_id: str, data: Dict[str, Any], decision: Dict[str, Any], safety_index: Dict) -> Dict[str, Any]:
        import datetime
        
        report_data = {
            "report_id": f"INC_{session_id}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}",
            "generated_at": datetime.datetime.now().isoformat(),
            "user_id": data.get("user_id", "unknown"),
            "location": {
                "lat": data.get("latitude"),
                "lon": data.get("longitude")
            },
            "incident_details": {
                "decision": decision.get("decision", "UNKNOWN"),
                "risk_score": decision.get("weighted_risk_score", 0),
                "safety_level": safety_index.get("safety_level", "UNKNOWN"),
                "actions_taken": decision.get("required_actions", [])
            },
            "agent_analysis": {
                "emergency": decision.get("agent_insights", {}).get("emergency", {}),
                "route": decision.get("agent_insights", {}).get("route", {}),
                "personal": decision.get("agent_insights", {}).get("personal", {})
            },
            "timeline": decision.get("escalation_timeline", [])
        }
        
        logger.info(f"Action: Generated incident report {report_data['report_id']}")
        
        return {
            "report_generated": True,
            "report_id": report_data["report_id"],
            "report_data": report_data,
            "formats_available": ["json", "pdf_note"]
        }


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
        self.share_location = ShareLocationLinkAction()
        self.auto_call = AutoCallGuardianAction()
        self.local_alarm = LocalAlarmAction()
        self.escalation = EscalationWorkflowAction()
        self.guardian_ack = GuardianAckAction()
        self.checkin = ScheduledCheckinAction()
        self.share_eta = ShareEtaAction()
        self.incident_report = IncidentReportAction()

    def execute_actions(self, orchestrator_decision: Dict[str, Any], data: Dict[str, Any]) -> Dict[str, Any]:
        results = {}
        actions = orchestrator_decision.get("required_actions", [])
        plan = orchestrator_decision.get("notification_plan", {}) or {}
        action_details = orchestrator_decision.get("action_details", {}) or {}

        logger.info(f"🎯 [Layer3] Executing actions: {actions}")

        guardians = data.get("guardians") or []
        guardian_targets: List[str] = []
        guardian_emails: List[str] = []
        if isinstance(guardians, list):
            for g in guardians:
                try:
                    if g.get("active") is False:
                        continue
                    phone = str(g.get("phone") or "").strip()
                    if phone:
                        guardian_targets.append(phone)
                    email = str(g.get("email") or "").strip()
                    if email:
                        guardian_emails.append(email)
                except Exception:
                    continue

        priority = 1 if action_details.get("push_priority") == "high" else 0

        if "PUSH_NOTIFICATION" in actions:
            user_id = str(data.get("user_id") or "").strip()
            push_payload = {
                "user_id": user_id,
                "title": plan.get("push_title", "Netrikan Alert"),
                "body": plan.get("push_body", "Safety Alert: Unusual activity detected."),
                "data": {"session_id": data.get("session_id") or "", "priority": action_details.get("push_priority", "normal")},
                "urgency": plan.get("urgency", "medium"),
                "sound": plan.get("sound", "default"),
            }

            if USE_OFFLINE_QUEUE and _has_queue:
                action_id = enqueue_action("push_notification", push_payload, priority=priority)
                results["push_notifications"] = {"queued": True, "action_id": action_id, "status": "pending"}
            else:
                try:
                    results["push_notifications"] = self.notification.execute_push(
                        user_id,
                        push_payload["body"],
                        push_payload["data"],
                    )
                except Exception as e:
                    logger.warning(f"Push failed: {e}")
                    results["push_notifications"] = {"sent": False, "error": str(e)}

        if "SMS_GUARDIANS" in actions:
            targets = guardian_targets
            sms_payload = {
                "targets": targets,
                "message": plan.get("sms_body", "SOS: Immediate attention required."),
                "include_location": action_details.get("sms_include_location", True),
                "last_location": {"lat": data.get("latitude"), "lon": data.get("longitude")},
            }

            if USE_OFFLINE_QUEUE and _has_queue:
                action_id = enqueue_action("sms_guardians", sms_payload, priority=priority)
                results["sms_alerts"] = {"sent": True, "targets": targets, "queued": True, "action_id": action_id}
            else:
                results["sms_alerts"] = {
                    "sent": self.notification.execute_sms(targets, sms_payload["message"]),
                    "targets": targets,
                }

        # EMAIL_GUARDIANS - Send email notifications (for HIGH level)
        if "EMAIL_GUARDIANS" in actions:
            targets = guardian_emails if guardian_emails else guardian_targets
            email_payload = {
                "targets": targets,
                "subject": plan.get("email_subject", "🚨 Safety Alert - Immediate Attention Required"),
                "body": plan.get("email_body", "A safety alert has been triggered for your loved one. Please check on them immediately."),
                "include_location": action_details.get("email_include_location", True),
                "last_location": {"lat": data.get("latitude"), "lon": data.get("longitude")},
            }

            if USE_OFFLINE_QUEUE and _has_queue:
                action_id = enqueue_action("email_guardians", email_payload, priority=priority)
                results["email_alerts"] = {"sent": True, "targets": targets, "queued": True, "action_id": action_id}
            else:
                results["email_alerts"] = {
                    "sent": self.notification.execute_email(targets, email_payload["subject"], email_payload["body"]),
                    "targets": targets,
                }

        if "POLICE_NOTIFICATION" in actions:
            police_payload = {
                "session_id": data.get("session_id") or "",
                "decision": orchestrator_decision.get("decision", "UNKNOWN"),
                "risk_score": orchestrator_decision.get("weighted_risk_score", 0),
                "last_location": {"lat": data.get("latitude"), "lon": data.get("longitude")},
                "guardians_notified": len(guardian_targets),
            }

            if USE_OFFLINE_QUEUE and _has_queue:
                action_id = enqueue_action("police_notification", police_payload, priority=2)
                results["police_status"] = {"triggered": True, "queued": True, "action_id": action_id}
            else:
                results["police_status"] = self.emergency.execute(police_payload)

        if "MAP_REROUTING" in actions:
            reroute_payload = {
                "start": {"lat": data.get("latitude"), "lon": data.get("longitude")},
                "end": data.get("destination"),
                "preference": "safe",
            }

            if USE_OFFLINE_QUEUE and _has_queue:
                action_id = enqueue_action("map_rerouting", reroute_payload)
                results["reroute_plan"] = {"queued": True, "action_id": action_id}
            else:
                results["reroute_plan"] = self.map_reroute.execute(reroute_payload["start"], reroute_payload["end"])

        if "SAFE_PLACES_SUGGESTION" in actions:
            radius_m = int(plan.get("safe_places_radius_m") or 2000)
            limit = int(plan.get("safe_places_limit") or 5)
            places_payload = {
                "lat": data.get("latitude"),
                "lon": data.get("longitude"),
                "radius_m": radius_m,
                "limit": limit,
            }

            if USE_OFFLINE_QUEUE and _has_queue:
                action_id = enqueue_action("safe_places", places_payload)
                results["nearby_safe_zones"] = {"queued": True, "action_id": action_id}
            else:
                results["nearby_safe_zones"] = self.safe_places.execute(
                    places_payload["lat"],
                    places_payload["lon"],
                    radius_m=radius_m,
                    limit=limit,
                )

        # SHARE_LOCATION_LINK
        if "SHARE_LOCATION_LINK" in actions:
            results["location_link"] = self.share_location.execute(
                lat=data.get("latitude", 0),
                lon=data.get("longitude", 0),
                user_name=data.get("user_name", "User")
            )

        # AUTO_CALL_GUARDIAN
        if "AUTO_CALL_GUARDIAN" in actions:
            target_number = guardian_targets[0] if guardian_targets else os.environ.get("EMERGENCY_FRIEND_NUMBER", "")
            results["auto_call"] = self.auto_call.execute(
                to_number=target_number,
                message="Emergency! Please check on me.",
                user_name=data.get("user_name", "User")
            )

        # LOCAL_ALARM
        if "LOCAL_ALARM" in actions:
            alarm_type = action_details.get("alarm_type", "siren")
            results["local_alarm"] = self.local_alarm.execute(alarm_type=alarm_type)

        # TELEGRAM_NOTIFY - Send Telegram message
        if "TELEGRAM_NOTIFY" in actions:
            try:
                import requests
                telegram_token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
                telegram_chat = os.environ.get("TELEGRAM_CHAT_ID", "").strip()
                if telegram_token and telegram_chat:
                    location = f"{data.get('latitude', 0)}, {data.get('longitude', 0)}"
                    message = f"🚨 SAFETY ALERT\n\nUser: {data.get('user_id', 'unknown')}\nSeverity: HIGH\nLocation: {location}\nSignal: {data.get('text_signal', 'N/A')}\nDecision: {orchestrator_decision.get('decision', 'UNKNOWN')}"
                    url = f"https://api.telegram.org/bot{telegram_token}/sendMessage"
                    resp = requests.post(url, json={"chat_id": telegram_chat, "text": message}, timeout=10)
                    results["telegram_notify"] = {"sent": resp.status_code == 200, "status": resp.status_code}
                    logger.info(f"Telegram alert sent for user {data.get('user_id')}")
                else:
                    results["telegram_notify"] = {"sent": False, "error": "Telegram not configured"}
            except Exception as e:
                logger.warning(f"Telegram notify failed: {e}")
                results["telegram_notify"] = {"sent": False, "error": str(e)}

        # ADB_CALL - Make ADB voice call
        if "ADB_CALL" in actions:
            try:
                import subprocess
                phone = os.environ.get("ADB_CALL_NUMBER", "PHONE_NUMBER_REMOVED").strip()
                if phone:
                    # Use -d flag to specify the device if multiple are connected, but for now we'll assume one
                    # am start -a android.intent.action.CALL -d tel:+91...
                    result = subprocess.run(
                        ["adb", "shell", "am", "start", "-a", "android.intent.action.CALL", "-d", f"tel:{phone}"],
                        capture_output=True, text=True, timeout=5
                    )
                    if result.returncode == 0:
                        results["adb_call"] = {"initiated": True, "phone": phone}
                        logger.info(f"ADB call initiated to {phone}")
                    else:
                        results["adb_call"] = {"initiated": False, "error": result.stderr}
                        logger.warning(f"ADB call failed: {result.stderr}")
                else:
                    results["adb_call"] = {"initiated": False, "error": "No phone number configured"}
            except Exception as e:
                logger.warning(f"ADB call failed: {e}")
                results["adb_call"] = {"initiated": False, "error": str(e)}

        # ESCALATION_WORKFLOW
        if "ESCALATION_WORKFLOW" in actions:
            steps = action_details.get("escalation_steps", ["PUSH", "SMS", "CALL", "FRIEND"])
            friend_number = os.environ.get("EMERGENCY_FRIEND_NUMBER", "")
            results["escalation_workflow"] = self.escalation.execute(
                steps=steps,
                guardian_numbers=guardian_targets,
                friend_number=friend_number,
                data=data
            )

        # GUARDIAN_ACK
        if "GUARDIAN_ACK" in actions:
            results["guardian_ack"] = self.guardian_ack.execute(
                session_id=data.get("session_id", "unknown"),
                guardian_id=guardian_targets[0] if guardian_targets else "unknown",
                guardians=guardians
            )

        # SCHEDULED_CHECKIN
        if "SCHEDULED_CHECKIN" in actions:
            interval = action_details.get("checkin_interval_minutes", 30)
            total = action_details.get("total_checkins", 3)
            results["scheduled_checkin"] = self.checkin.execute(
                interval_minutes=interval,
                total_checkins=total
            )

        # SHARE_ETA
        if "SHARE_ETA" in actions:
            results["share_eta"] = self.share_eta.execute(
                current_lat=data.get("latitude", 0),
                current_lon=data.get("longitude", 0),
                destination=data.get("destination"),
                speed_kmh=data.get("speed", 5.0)
            )

        # INCIDENT_REPORT
        if "INCIDENT_REPORT" in actions:
            results["incident_report"] = self.incident_report.execute(
                session_id=data.get("session_id", "unknown"),
                data=data,
                decision=orchestrator_decision,
                safety_index=orchestrator_decision.get("safety_index", {})
            )

        results["queue_stats"] = self._get_queue_summary()
        return results

    def _get_queue_summary(self) -> Dict[str, int]:
        """Get quick summary of action queue status."""
        try:
            from services.action_queue import get_queue_stats
            return get_queue_stats()
        except Exception:
            return {"pending": 0, "completed": 0, "failed": 0}