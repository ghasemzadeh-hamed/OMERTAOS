# OMERTAOS Canonical Structure

- `kernel`
- `control`
- `data`
- `services`
- `interface`
- `shared`
- `infra`
- `runtime-daemon`

Notes:
- OS-level execution/isolation/sandbox responsibilities live in `runtime-daemon`.
- Python layers call runtime daemon through `control_plane/runtime_client.py`.
- gRPC IPC contract lives in `shared/proto/runtime.proto`.
