import sqlite3
import json
import threading
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path
from utils.logger import get_logger

logger = get_logger("ActionQueue")

DB_PATH = "/tmp/netrikan_actions.db"

_action_lock = threading.Lock()


def _init_db():
    """Initialize the SQLite database for action queue."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS pending_actions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            action_type TEXT NOT NULL,
            payload TEXT NOT NULL,
            priority INTEGER DEFAULT 0,
            created_at TEXT NOT NULL,
            retry_count INTEGER DEFAULT 0,
            last_error TEXT,
            status TEXT DEFAULT 'pending'
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS action_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            action_type TEXT NOT NULL,
            payload TEXT NOT NULL,
            status TEXT NOT NULL,
            result TEXT,
            completed_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


_init_db()


def enqueue_action(action_type: str, payload: Dict[str, Any], priority: int = 0) -> int:
    """Add an action to the queue."""
    with _action_lock:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO pending_actions (action_type, payload, priority, created_at, status)
               VALUES (?, ?, ?, ?, 'pending')""",
            (action_type, json.dumps(payload), priority, datetime.now().isoformat())
        )
        action_id = cursor.lastrowid
        conn.commit()
        conn.close()
        logger.info(f"Action queued: {action_type} (id={action_id})")
        return action_id


def get_pending_actions(limit: int = 10) -> List[Dict[str, Any]]:
    """Get pending actions ordered by priority and creation time."""
    with _action_lock:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            """SELECT * FROM pending_actions 
               WHERE status = 'pending' 
               ORDER BY priority DESC, created_at ASC 
               LIMIT ?""",
            (limit,)
        )
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]


def mark_action_completed(action_id: int, result: Optional[Dict[str, Any]] = None):
    """Mark an action as completed and move to history."""
    with _action_lock:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Get the action details before moving
        cursor.execute("SELECT * FROM pending_actions WHERE id = ?", (action_id,))
        row = cursor.fetchone()
        if row:
            # Move to history
            cursor.execute(
                """INSERT INTO action_history (action_type, payload, status, result, completed_at)
                   VALUES (?, ?, 'completed', ?, ?)""",
                (row[1], row[2], json.dumps(result or {}), datetime.now().isoformat())
            )
            # Delete from pending
            cursor.execute("DELETE FROM pending_actions WHERE id = ?", (action_id,))
        
        conn.commit()
        conn.close()
        logger.info(f"Action completed: id={action_id}")


def mark_action_failed(action_id: int, error: str, max_retries: int = 3):
    """Mark an action as failed, increment retry count."""
    with _action_lock:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("SELECT retry_count FROM pending_actions WHERE id = ?", (action_id,))
        row = cursor.fetchone()
        
        if row and row[0] >= max_retries:
            # Move to history as failed
            cursor.execute("SELECT * FROM pending_actions WHERE id = ?", (action_id,))
            action_row = cursor.fetchone()
            if action_row:
                cursor.execute(
                    """INSERT INTO action_history (action_type, payload, status, result, completed_at)
                       VALUES (?, ?, 'failed', ?, ?)""",
                    (action_row[1], action_row[2], json.dumps({"error": error}), datetime.now().isoformat())
                )
            cursor.execute("DELETE FROM pending_actions WHERE id = ?", (action_id,))
            logger.warning(f"Action failed after max retries: id={action_id}")
        else:
            # Increment retry count
            cursor.execute(
                """UPDATE pending_actions 
                   SET retry_count = retry_count + 1, last_error = ?, status = 'pending' 
                   WHERE id = ?""",
                (error, action_id)
            )
            logger.warning(f"Action failed, will retry: id={action_id}, error={error[:100]}")
        
        conn.commit()
        conn.close()


def get_queue_stats() -> Dict[str, int]:
    """Get queue statistics."""
    with _action_lock:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM pending_actions WHERE status = 'pending'")
        pending = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM action_history WHERE status = 'completed'")
        completed = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM action_history WHERE status = 'failed'")
        failed = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "pending": pending,
            "completed": completed,
            "failed": failed,
            "total": pending + completed + failed
        }


def clear_completed_actions(days_old: int = 7):
    """Clear old completed actions from history."""
    with _action_lock:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            """DELETE FROM action_history 
               WHERE status = 'completed' 
               AND completed_at < datetime('now', '-' || ? || ' days')""",
            (days_old,)
        )
        deleted = cursor.rowcount
        conn.commit()
        conn.close()
        logger.info(f"Cleared {deleted} old completed actions")
        return deleted