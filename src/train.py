"""Temporary compatibility adapter; implementation: llm_training.train."""
import importlib
import sys
_impl = importlib.import_module('llm_training.train')
sys.modules[__name__] = _impl
