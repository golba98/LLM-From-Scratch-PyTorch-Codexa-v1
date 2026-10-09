"""Temporary compatibility adapter; implementation: llm_training.training."""
import importlib
import sys
_impl = importlib.import_module('llm_training.training')
sys.modules[__name__] = _impl
