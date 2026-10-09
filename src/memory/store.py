"""Temporary compatibility adapter; implementation: llm_memory.store."""
import importlib
import sys
_impl = importlib.import_module('llm_memory.store')
sys.modules[__name__] = _impl
