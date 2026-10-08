"""Temporary compatibility adapter; implementation: llm_data.token_data."""
import importlib
import sys
_impl = importlib.import_module('llm_data.token_data')
sys.modules[__name__] = _impl
