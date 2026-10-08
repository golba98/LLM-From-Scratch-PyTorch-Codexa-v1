"""Compatibility alias for the integration evaluation API."""
import sys
from codexa_workspace import evaluation as _implementation
sys.modules[__name__] = _implementation
