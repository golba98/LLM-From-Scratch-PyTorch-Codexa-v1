"""Temporary compatibility adapter; implementation: llm_data.data.general_chat."""
import importlib
import sys
_impl = importlib.import_module('llm_data.data.general_chat')
sys.modules[__name__] = _impl
