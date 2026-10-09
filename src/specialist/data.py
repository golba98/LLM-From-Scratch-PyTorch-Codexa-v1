"""Temporary compatibility adapter; implementation: llm_specialist.data."""
import importlib
import sys
_impl = importlib.import_module('llm_specialist.data')
sys.modules[__name__] = _impl
