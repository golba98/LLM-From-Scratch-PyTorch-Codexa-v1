"""Temporary compatibility adapter; implementation: llm_data.data.split."""
import importlib
import sys
_impl = importlib.import_module('llm_data.data.split')
sys.modules[__name__] = _impl
