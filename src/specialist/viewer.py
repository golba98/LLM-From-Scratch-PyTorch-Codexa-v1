"""Temporary compatibility adapter; implementation: llm_specialist.viewer."""
import importlib
import sys
_impl = importlib.import_module('llm_specialist.viewer')
sys.modules[__name__] = _impl
