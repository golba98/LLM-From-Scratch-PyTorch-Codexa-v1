"""Temporary compatibility adapter; implementation: llm_data.data.cleaning."""
import importlib
import sys
_impl = importlib.import_module('llm_data.data.cleaning')
sys.modules[__name__] = _impl
