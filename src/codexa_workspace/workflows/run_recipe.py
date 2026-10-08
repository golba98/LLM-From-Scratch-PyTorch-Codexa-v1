"""Resolve historical recipes explicitly, keeping old artifacts read-only."""

import argparse
import json
from pathlib import Path
import subprocess
import sys

from codexa_workspace.assets import workspace_root, asset_root, resolve_input
ROOT = workspace_root()
INPUT_FLAGS = {
    "--checkpoint", "--init-checkpoint", "--tokenizer", "--train-jsonl", "--validation-jsonl",
    "--train-token-file", "--validation-token-file", "--base-token-file", "--token-manifest",
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("recipe")
    parser.add_argument("--describe", action="store_true")
    args = parser.parse_args()
    recipes = json.loads((ROOT / "workflows/recipes.json").read_text())
    if args.recipe not in recipes:
        parser.error("Unknown recipe: " + args.recipe)
    recipe = recipes[args.recipe]
    artifact_root = asset_root(ROOT)
    resolved = recipe["arguments"].copy()
    inputs = []
    for index, flag in enumerate(resolved[:-1]):
        if flag in INPUT_FLAGS:
            path = Path(resolved[index + 1])
            path = resolve_input(ROOT, path)
            resolved[index + 1] = str(path)
            inputs.append(path)
    if args.describe:
        print(json.dumps(dict(command=recipe["command"], arguments=resolved,
                              missing_inputs=[str(p) for p in inputs if not p.is_file()]), indent=2))
        return 0
    missing = [str(p) for p in inputs if not p.is_file()]
    if missing:
        parser.error("Historical inputs are unavailable; no training launched: " + ", ".join(missing))
    return subprocess.call([sys.executable, str(ROOT / "run.py"), recipe["command"], *resolved])


if __name__ == "__main__":
    raise SystemExit(main())
