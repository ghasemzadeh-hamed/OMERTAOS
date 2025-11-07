"""Expose generated protobuf modules under the :mod:`aion.v1` namespace."""

from __future__ import annotations

from importlib import import_module

tasks_pb2 = import_module("os.control.aion_grpc.aion.v1.tasks_pb2")
tasks_pb2_grpc = import_module("os.control.aion_grpc.aion.v1.tasks_pb2_grpc")

__all__ = ["tasks_pb2", "tasks_pb2_grpc"]
