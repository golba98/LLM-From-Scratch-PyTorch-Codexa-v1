"""Temporary compatibility adapter; implementation: llm_specialist.config."""
import importlib
import sys
_impl = importlib.import_module('llm_specialist.config')
sys.modules[__name__] = _impl
