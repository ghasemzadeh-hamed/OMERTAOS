from __future__ import annotations

from pathlib import Path

from shared.generated.python.aion.v1 import tasks_pb2

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_canonical_proto_sources_are_versioned_and_complete() -> None:
    root = REPO_ROOT / "schemas" / "v1" / "protos"
    sources = sorted(path.relative_to(root).as_posix() for path in root.rglob("*.proto"))

    assert sources == ["aion/v1/tasks.proto", "runtime.proto"]
    task_source = (root / "aion/v1/tasks.proto").read_text(encoding="utf-8")
    runtime_source = (root / "runtime.proto").read_text(encoding="utf-8")
    assert "service AionTasks" in task_source
    assert "service RuntimeService" in runtime_source


def test_legacy_proto_and_json_aliases_are_absent() -> None:
    retired = (
        "schemas/config",
        "schemas/events",
        "schemas/proto",
        "schemas/protos",
        "schemas/result.schema.json",
        "schemas/task.schema.json",
        "shared/proto",
        "schemas/v1/protos/python",
    )
    violations = [path for path in retired if (REPO_ROOT / path).exists()]
    assert not violations, f"retired schema aliases remain: {violations}"


def test_recovered_python_binding_round_trips_wire_messages() -> None:
    request = tasks_pb2.TaskRequest(
        schema_version="1.0",
        task_id="task-1",
        intent="status",
        params={"key": "value"},
        request_id="request-1",
    )
    recovered = tasks_pb2.TaskRequest.FromString(request.SerializeToString())

    assert recovered == request
    service = tasks_pb2.DESCRIPTOR.services_by_name["AionTasks"]
    assert [method.name for method in service.methods] == ["Submit", "Stream", "AckStream", "StatusById"]


def test_build_and_gateway_references_use_canonical_proto_tree() -> None:
    expected = {
        "runtime-daemon/build.rs": "../schemas/v1/protos/runtime.proto",
        "runtime-daemon/Dockerfile": "COPY schemas/v1/protos ./schemas/v1/protos",
        "gateway/Dockerfile": "COPY schemas/v1/protos ./protos",
        "deploy/docker/compose/local.yml": "./schemas/v1/protos:/protos:ro",
    }
    for path, reference in expected.items():
        assert reference in (REPO_ROOT / path).read_text(encoding="utf-8")

    resolver = (REPO_ROOT / "gateway/src/protoPath.ts").read_text(encoding="utf-8")
    assert "schemas/v1/protos" in resolver
    assert "AION_PROTO_ROOT" in resolver


def test_schema_compatibility_wrappers_do_not_import_removed_namespace() -> None:
    roots = (REPO_ROOT / "shared" / "generated" / "python",)
    violations = [
        str(path.relative_to(REPO_ROOT))
        for root in roots
        for path in root.rglob("*.py")
        if "os.control" in path.read_text(encoding="utf-8")
    ]
    assert not violations
