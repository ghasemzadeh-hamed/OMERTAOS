"""Compatibility export; new code imports from control.transports.grpc."""

from control.transports.grpc import GrpcAdapter, GrpcTransportUnavailable

__all__ = ["GrpcAdapter", "GrpcTransportUnavailable"]
