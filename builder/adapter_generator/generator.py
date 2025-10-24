"""Generates WASM/gRPC adapters from vendor specifications."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict
from uuid import uuid4

from jinja2 import Environment, FileSystemLoader


class AdapterGenerator:
    """Create adapter projects and produce metadata for registration."""

    def __init__(self, output_dir: Path) -> None:
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        template_dir = Path(__file__).parent / "templates"
        self.env = Environment(loader=FileSystemLoader(str(template_dir)))

    def generate(self, spec: Dict[str, object]) -> Dict[str, object]:
        protocol = spec.get("protocol", "rest")
        if protocol not in {"rest", "grpc"}:
            raise ValueError("Unsupported protocol")
        adapter_id = uuid4().hex[:12]
        module_dir = self.output_dir / f"{spec['name']}-{adapter_id}"
        module_dir.mkdir(parents=True, exist_ok=True)
        manifest = self._render_manifest(module_dir, spec)
        code_path = self._render_adapter(module_dir, spec)
        sbom_path = self._write_sbom(module_dir, spec)
        return {
            "adapter_id": adapter_id,
            "module_dir": str(module_dir),
            "manifest": manifest,
            "entrypoint": str(code_path),
            "sbom": str(sbom_path),
        }

    def _render_manifest(self, module_dir: Path, spec: Dict[str, object]) -> str:
        manifest_template = self.env.get_template("manifest.yaml.j2")
        manifest = manifest_template.render(spec=spec)
        path = module_dir / "manifest.yaml"
        path.write_text(manifest)
        return str(path)

    def _render_adapter(self, module_dir: Path, spec: Dict[str, object]) -> Path:
        template_name = "adapter_rest.rs.j2" if spec["protocol"] == "rest" else "adapter_grpc.rs.j2"
        template = self.env.get_template(template_name)
        rendered = template.render(spec=spec)
        path = module_dir / "src" / "lib.rs"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(rendered)
        return path

    def _write_sbom(self, module_dir: Path, spec: Dict[str, object]) -> Path:
        sbom = {
            "name": spec["name"],
            "version": spec["version"],
            "generated_at": json.dumps(spec, sort_keys=True),
        }
        path = module_dir / "sbom.json"
        path.write_text(json.dumps(sbom, indent=2))
        return path
