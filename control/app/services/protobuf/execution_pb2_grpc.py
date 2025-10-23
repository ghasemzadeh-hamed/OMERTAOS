# Generated manually to match execution.proto service
from __future__ import annotations

import grpc

from . import execution_pb2 as execution__pb2


class TaskModuleStub(object):
    def __init__(self, channel: grpc.aio.Channel):
        self.Execute = channel.unary_unary(
            '/aion.execution.TaskModule/Execute',
            request_serializer=execution__pb2.TaskRequest.SerializeToString,
            response_deserializer=execution__pb2.TaskReply.FromString,
        )


class TaskModuleServicer(object):
    async def Execute(self, request, context):  # pragma: no cover - to be implemented on server
        context.set_details('Method not implemented!')
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        raise NotImplementedError('Execute method not implemented!')


def add_TaskModuleServicer_to_server(servicer, server):
    rpc_method_handlers = {
        'Execute': grpc.aio.unary_unary_rpc_method_handler(
            servicer.Execute,
            request_deserializer=execution__pb2.TaskRequest.FromString,
            response_serializer=execution__pb2.TaskReply.SerializeToString,
        ),
    }
    generic_handler = grpc.aio.method_handlers_generic_handler(
        'aion.execution.TaskModule', rpc_method_handlers
    )
    server.add_generic_rpc_handlers((generic_handler,))
