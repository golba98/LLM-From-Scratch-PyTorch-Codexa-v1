"""Temporary compatibility adapter; implementation: llm_data.data.statistics."""
import importlib
import sys
_impl = importlib.import_module('llm_data.data.statistics')
sys.modules[__name__] = _impl
