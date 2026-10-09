"""Temporary compatibility adapter; implementation: llm_training.hardware_monitor."""
import importlib
import sys
_impl = importlib.import_module('llm_training.hardware_monitor')
sys.modules[__name__] = _impl
