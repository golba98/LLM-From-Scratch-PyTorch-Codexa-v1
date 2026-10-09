"""Source development paths for the root and its explicitly pinned submodules."""
import json
import os
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parent
manifest = json.loads((ROOT / "compatibility.json").read_text())
PATHS = [str(ROOT / item["path"] / "src") for item in manifest["components"].values()]
PATHS.extend([str(ROOT / "src"), str(ROOT)])
for path in reversed(PATHS):
    if path not in sys.path:
        sys.path.insert(0, path)
os.environ["CODEXA_WORKSPACE_ROOT"] = str(ROOT)
os.environ["PYTHONPATH"] = os.pathsep.join(dict.fromkeys([*PATHS, *filter(None, os.environ.get("PYTHONPATH", "").split(os.pathsep))]))
