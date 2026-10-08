"""Temporary compatibility adapter; implementation: llm_data.data.io."""
import importlib
import sys
_impl = importlib.import_module('llm_data.data.io')
sys.modules[__name__] = _impl
