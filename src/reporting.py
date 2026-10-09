"""Temporary compatibility adapter; implementation: llm_training.reporting."""
import importlib
import sys
_impl = importlib.import_module('llm_training.reporting')
sys.modules[__name__] = _impl
