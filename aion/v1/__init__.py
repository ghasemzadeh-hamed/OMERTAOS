"""Compatibility namespace exposing protobuf stubs under ``aion.v1``.

This package re-exports the generated gRPC bindings that ship inside the
control service so legacy imports (e.g. ``from aion.v1 import tasks_pb2``)
continue to work after the project restructuring.
"""

from importlib import import_module
from types import ModuleType
from typing import List

__all__: List[str] = ["tasks_pb2", "tasks_pb2_grpc"]


def _load(name: str) -> ModuleType:
    return import_module(f"aion.v1.{name}")


def __getattr__(name: str) -> ModuleType:
    if name not in __all__:
        raise AttributeError(name)
    module = _load(name)
    globals()[name] = module
    return module
