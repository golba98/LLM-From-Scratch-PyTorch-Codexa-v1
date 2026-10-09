"""Temporary compatibility adapter; implementation: llm_data.data.governance."""
import importlib
import sys
_impl = importlib.import_module('llm_data.data.governance')
sys.modules[__name__] = _impl
