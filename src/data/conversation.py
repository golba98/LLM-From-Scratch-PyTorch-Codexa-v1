"""Temporary compatibility adapter; implementation: llm_data.data.conversation."""
import importlib
import sys
_impl = importlib.import_module('llm_data.data.conversation')
sys.modules[__name__] = _impl
