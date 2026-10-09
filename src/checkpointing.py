"""Temporary compatibility adapter; implementation: llm_training.checkpointing."""
import importlib
import sys
_impl = importlib.import_module('llm_training.checkpointing')
sys.modules[__name__] = _impl
