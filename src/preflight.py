"""Temporary compatibility adapter; implementation: llm_training.preflight."""
import importlib
import sys
_impl = importlib.import_module('llm_training.preflight')
sys.modules[__name__] = _impl
