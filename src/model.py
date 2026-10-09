"""Temporary compatibility adapter; implementation: llm_architecture.model."""
import importlib
import sys
_impl = importlib.import_module('llm_architecture.model')
sys.modules[__name__] = _impl
