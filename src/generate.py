"""Temporary compatibility adapter; implementation: llm_inference.generate."""
import importlib
import sys
_impl = importlib.import_module('llm_inference.generate')
sys.modules[__name__] = _impl
