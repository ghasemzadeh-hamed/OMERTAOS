"""Lazy registry for optional machine-learning integrations."""
from __future__ import annotations

from importlib import import_module

_DEFAULT_HINT = "see pyproject optional-dependencies"


class LazyModule:
    """Descriptor for lazily importing optional modules."""

    def __init__(self, import_path: str, extra_hint: str | None = None):
        self.import_path = import_path
        self.extra_hint = extra_hint or ""
        self._mod = None

    @property
    def module(self):
        """Import the module on demand, raising a helpful error if missing."""
        if self._mod is None:
            try:
                self._mod = import_module(self.import_path)
            except ModuleNotFoundError as exc:  # pragma: no cover - exercised via API
                hint = self.extra_hint or _DEFAULT_HINT
                raise RuntimeError(
                    f"Module '{self.import_path}' not installed. Install extras: {hint}"
                ) from exc
        return self._mod


REGISTRY: dict[str, LazyModule] = {
    "pyro": LazyModule("pyro", "pip install .[ml-ppl]"),
    "cvxpy": LazyModule("cvxpy", "pip install .[ml-optim]"),
    "cvxpylayers": LazyModule("cvxpylayers", "pip install .[ml-optim]"),
    "stumpy": LazyModule(
        "aionos_control.plugins.entries.stumpy_entry",
        "pip install .[ml-timeseries]",
    ),
    "cleanlab": LazyModule(
        "aionos_control.plugins.entries.cleanlab_entry",
        "pip install .[ml-explain]",
    ),
    "hypertools": LazyModule("hypertools", "pip install .[ml-graphviz]"),
    "pygwalker": LazyModule("pygwalker", "pip install .[ml-graphviz]"),
    "featuretools": LazyModule("featuretools", "pip install .[ml-features]"),
    "shapash": LazyModule("shapash", "pip install .[ml-explain]"),
    "aix360": LazyModule("aix360", "pip install .[ml-explain]"),
    "pycaret": LazyModule("pycaret", "pip install .[ml-automl]"),
    "taipy": LazyModule("taipy", "pip install .[ml-ui]"),
    "pysindy": LazyModule("pysindy", "pip install .[ml-timeseries]"),
    "reloading": LazyModule("reloading", "pip install reloading"),
    "mitoinstaller": LazyModule("mitoinstaller", "pip install .[notebook-addons]"),
    "mito": LazyModule("mitosheet", "pip install .[notebook-addons]"),
    "nevergrad": LazyModule(
        "aionos_control.plugins.entries.nevergrad_entry",
        "pip install .[ml-optim]",
    ),
}

__all__ = ["LazyModule", "REGISTRY", "_DEFAULT_HINT"]
