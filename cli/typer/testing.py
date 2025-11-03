"""Proxy testing helpers for the Typer shim when importing via CLI path."""

from __future__ import annotations

from importlib import import_module

_testing = import_module("_aion_typer_shim").testing  # type: ignore[attr-defined]

__all__ = getattr(_testing, "__all__", []) or ["CliRunner"]

CliRunner = getattr(_testing, "CliRunner")
