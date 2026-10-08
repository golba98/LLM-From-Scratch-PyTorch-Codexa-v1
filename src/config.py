"""Temporary compatibility adapter; implementation: llm_training.config."""
import importlib
import sys
_impl = importlib.import_module('llm_training.config')
sys.modules[__name__] = _impl
