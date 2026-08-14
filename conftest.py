"""Ensure the OMERTA OS compatibility shim is installed during tests."""

from __future__ import annotations

import importlib
import sys

if "sitecustomize" not in sys.modules:
    importlib.import_module("sitecustomize")
