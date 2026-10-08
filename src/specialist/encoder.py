"""Temporary compatibility adapter; implementation: llm_specialist.encoder."""
import importlib
import sys
_impl = importlib.import_module('llm_specialist.encoder')
sys.modules[__name__] = _impl
