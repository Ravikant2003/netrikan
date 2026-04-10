from __future__ import annotations

import os
import sys
from pathlib import Path


# Ensure `backend/` is on sys.path so imports like `import core...` work
# even when tests are executed via a console-script entrypoint.
BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

# Gemini-only mode requires a key at import-time. For tests we provide a dummy.
os.environ.setdefault("GEMINI_API_KEY", "test-key")
