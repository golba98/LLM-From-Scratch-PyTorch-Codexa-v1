"""Temporary compatibility adapter; implementation: llm_tokenizer.tokenizer."""
import importlib
import sys
_impl = importlib.import_module('llm_tokenizer.tokenizer')
sys.modules[__name__] = _impl
