"""Temporary compatibility adapter; implementation: llm_memory.service."""
import importlib
import sys
_impl = importlib.import_module('llm_memory.service')
sys.modules[__name__] = _impl
