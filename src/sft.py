"""Temporary compatibility adapter; implementation: llm_tokenizer.sft."""
import importlib
import sys
_impl = importlib.import_module('llm_tokenizer.sft')
sys.modules[__name__] = _impl
