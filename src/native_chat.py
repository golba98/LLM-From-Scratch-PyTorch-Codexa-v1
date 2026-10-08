"""Temporary compatibility adapter; implementation: llm_inference.native_chat."""
import importlib
import sys
_impl = importlib.import_module('llm_inference.native_chat')
sys.modules[__name__] = _impl
