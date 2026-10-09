"""Temporary compatibility adapter; implementation: llm_inference.context."""
import importlib
import sys
_impl = importlib.import_module('llm_inference.context')
sys.modules[__name__] = _impl
