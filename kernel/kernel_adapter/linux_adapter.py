from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence


@dataclass(frozen=True)
class SpawnSpec:
    argv: tuple[str, ...]
    seccomp_profile: str
    no_new_privileges: bool = True
    read_only_fs: bool = True


class LinuxKernelAdapter:
    def spawn(self, spec: SpawnSpec) -> dict[str, object]:
        return {"argv": list(spec.argv), "seccomp_profile": spec.seccomp_profile, "delegated": True}


def build_docker_spawn(image: str, command: Sequence[str], seccomp_profile: str, mounts: Sequence[str], cpu: str, memory: str, cap_drop_all: bool = True) -> SpawnSpec:
    argv: list[str] = [
        "docker",
        "run",
        "--rm",
        "--network",
        "none",
        "--security-opt",
        f"seccomp={seccomp_profile}",
        "--security-opt",
        "no-new-privileges",
        "--read-only",
        "--cpus",
        cpu,
        "--memory",
        memory,
        "--user",
        "65534:65534",
    ]
    if cap_drop_all:
        argv.extend(["--cap-drop", "ALL"])
    for mount in mounts:
        argv.extend(["-v", mount])
    argv.append(image)
    argv.extend(command)
    return SpawnSpec(argv=tuple(argv), seccomp_profile=seccomp_profile)
