"""Temporary compatibility adapter; implementation: llm_training.conversational_training."""
import importlib
import sys
_impl = importlib.import_module('llm_training.conversational_training')
sys.modules[__name__] = _impl
