"""
Background action processor for offline queue.
Can be run as a background task to process pending actions.
"""
import asyncio
import threading
import time
from services.action_queue import get_pending_actions, mark_action_completed, mark_action_failed
from services.notifiers import get_notifier
from utils.logger import get_logger

logger = get_logger("ActionProcessor")

_processing = False
_processing_thread = None
_stop_event = threading.Event()


async def process_action(action_type: str, payload: dict) -> dict:
    """Process a single action based on its type."""
    notifier = get_notifier()
    
    if action_type == "push_notification":
        user_id = payload.get("user_id", "")
        title = payload.get("title", "Netrikan Alert")
        body = payload.get("body", "Safety Alert")
        data = payload.get("data", {})
        await notifier.send_push(user_id, title, body, data)
        return {"status": "sent", "type": "push"}
    
    elif action_type == "sms_guardians":
        targets = payload.get("targets", [])
        message = payload.get("message", "Safety alert")
        for target in targets:
            await notifier.send_sms(target, message)
        return {"status": "sent", "type": "sms", "targets": len(targets)}
    
    elif action_type == "police_notification":
        await notifier.notify_police(payload)
        return {"status": "sent", "type": "police"}
    
    elif action_type == "map_rerouting":
        # This is synchronous, just return success
        return {"status": "processed", "type": "reroute"}
    
    elif action_type == "safe_places":
        # This is synchronous, just return success
        return {"status": "processed", "type": "safe_places"}
    
    else:
        return {"status": "unknown_action_type", "type": action_type}


def process_pending_actions(max_actions: int = 10) -> dict:
    """Process pending actions from the queue."""
    global _processing
    
    if _processing:
        return {"status": "already_processing"}
    
    _processing = True
    processed = 0
    failed = 0
    
    try:
        pending = get_pending_actions(limit=max_actions)
        logger.info(f"Processing {len(pending)} pending actions")
        
        for action in pending:
            action_id = action["id"]
            action_type = action["action_type"]
            payload_str = action["payload"]
            
            try:
                import json
                payload = json.loads(payload_str)
                
                result = asyncio.run(process_action(action_type, payload))
                mark_action_completed(action_id, result)
                processed += 1
                logger.info(f"Processed action {action_id}: {action_type}")
                
            except Exception as e:
                logger.error(f"Failed to process action {action_id}: {e}")
                mark_action_failed(action_id, str(e))
                failed += 1
        
    except Exception as e:
        logger.error(f"Error processing actions: {e}")
    finally:
        _processing = False
    
    return {
        "processed": processed,
        "failed": failed,
        "total": len(pending)
    }


def start_background_processor(interval_seconds: int = 30, max_actions: int = 10):
    """Start a background thread to process actions periodically."""
    global _processing_thread
    
    _stop_event.clear()
    
    def run():
        while not _stop_event.is_set():
            try:
                result = process_pending_actions(max_actions)
                if result.get("processed", 0) > 0:
                    logger.info(f"Background processor: {result}")
            except Exception as e:
                logger.error(f"Background processor error: {e}")
            _stop_event.wait(interval_seconds)
    
    _processing_thread = threading.Thread(target=run, daemon=True)
    _processing_thread.start()
    logger.info(f"Background action processor started (interval: {interval_seconds}s)")
    return _processing_thread


def stop_background_processor():
    """Stop the background processor."""
    global _processing_thread
    if _processing_thread and _processing_thread.is_alive():
        _stop_event.set()
        _processing_thread.join(timeout=5)
        _processing_thread = None
        logger.info("Background action processor stopped")