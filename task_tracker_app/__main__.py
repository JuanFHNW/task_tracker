"""Entry point: python -m task_tracker_app"""

import sys
from pathlib import Path

# Ensure imports resolve from this project root
root = Path(__file__).resolve().parent.parent
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

from task_tracker_app.application import TaskApplication

if __name__ in {"__main__", "__mp_main__"}:
    app = TaskApplication()
    app.run(host="127.0.0.1", port=8080, reload=True)