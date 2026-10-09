"""Temporary compatibility adapter; implementation: llm_specialist.artifacts."""
import importlib
import sys
_impl = importlib.import_module('llm_specialist.artifacts')
sys.modules[__name__] = _impl
