"""Temporary compatibility adapter; implementation: llm_specialist.training."""
import importlib
import sys
_impl = importlib.import_module('llm_specialist.training')
sys.modules[__name__] = _impl
