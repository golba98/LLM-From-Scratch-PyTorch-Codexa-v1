"""Temporary compatibility adapter; implementation: llm_data.data.mixture."""
import importlib
import sys
_impl = importlib.import_module('llm_data.data.mixture')
sys.modules[__name__] = _impl
