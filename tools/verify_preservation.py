"""Verify configured recovery records and relocated assets without reading weights by default."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--full", action="store_true", help="Stream every asset's SHA-256 again.")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    settings = json.loads((root / "artifacts.local.json").read_text())
    recovery = Path(settings["recovery_root"])
    records = json.loads((recovery / "asset-manifest.json").read_text())
    for record in records:
        path = Path(record["destination"])
        stat = path.stat()
        if stat.st_size != record["bytes"] or stat.st_mtime_ns != record["mtime_ns"]:
            raise ValueError(f"Historical asset metadata changed: {path}")
        if args.full:
            with path.open("rb") as handle:
                digest = hashlib.file_digest(handle, "sha256").hexdigest()
            if digest != record["sha256"]:
                raise ValueError(f"Historical asset hash changed: {path}")
    repositories = json.loads((recovery / "repositories.json").read_text())
    for repository in repositories:
        subprocess.run(["git", "bundle", "verify", str(Path(repository["recovery"]) / "history.bundle")], cwd=root, check=True, capture_output=True)
    result = {"files": len(records), "bytes": sum(r["bytes"] for r in records), "metadata_verified": True,
              "sha256_rechecked_this_run": args.full, "prior_full_verification": json.loads((recovery / "asset-verification.json").read_text()),
              "repository_bundles": len(repositories), "independent_backup": False}
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
