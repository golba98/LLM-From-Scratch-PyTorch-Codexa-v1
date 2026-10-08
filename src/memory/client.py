"""Temporary compatibility adapter; implementation: llm_memory.client."""
import importlib
import sys
_impl = importlib.import_module('llm_memory.client')
sys.modules[__name__] = _impl
