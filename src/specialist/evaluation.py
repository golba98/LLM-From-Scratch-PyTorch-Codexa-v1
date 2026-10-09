"""Temporary compatibility adapter; implementation: llm_specialist.evaluation."""
import importlib
import sys
_impl = importlib.import_module('llm_specialist.evaluation')
sys.modules[__name__] = _impl
