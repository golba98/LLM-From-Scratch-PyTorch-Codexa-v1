"""Temporary compatibility adapter; implementation: llm_specialist.models."""
import importlib
import sys
_impl = importlib.import_module('llm_specialist.models')
sys.modules[__name__] = _impl
