# Workflows

Stage 2 and overfit Python workflows remain central. Operator-launched base/SFT commands attach the required 100x22 Kitty viewer before training; Stage 2 retains its own visible attachment gate. No training was launched during extraction.

legacy/ preserves the original shell recipes verbatim. Launching script wrappers now invoke run_recipe, which resolves read-only inputs through the artifact catalog, removes implicit legacy resume and overwrite flags, and uses fresh `-workspace` output names. Missing historical inputs stop before training. These recipes are historical experiments, not recommendations to rerun them or promote a model. No checkpoint or dataset symlinks are used.

Use `python run.py module workflows.run_recipe <recipe> --describe` to inspect resolved arguments without launching anything. Prefer explicit current configs and artifact paths for new experiments.
