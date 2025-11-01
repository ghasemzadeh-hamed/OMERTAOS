import shutil
import sys
import tarfile
from pathlib import Path

import pytest
from typer.testing import CliRunner

CLI_DIR = Path(__file__).resolve().parents[1] / "cli"
if str(CLI_DIR) not in sys.path:
    sys.path.insert(0, str(CLI_DIR))

from aion.cli import app  # type: ignore  # noqa: E402


def _build_bundle_archive(tmp_path: Path) -> Path:
    source_dir = Path(__file__).resolve().parents[1] / "deploy/bundles/example/my-config"
    work_dir = tmp_path / "my-config"
    shutil.copytree(source_dir, work_dir)
    (work_dir / "VERSION").write_text("0.1.0\n", encoding="utf-8")
    (work_dir / "CHECKSUMS.txt").write_text("demo\n", encoding="utf-8")
    services_dir = work_dir / "services"
    services_dir.mkdir(parents=True, exist_ok=True)
    (services_dir / "aion-control.service").write_text(
        """[Unit]\nDescription=AION Control\n[Service]\nExecStart=/usr/bin/env true\n[Install]\nWantedBy=multi-user.target\n""",
        encoding="utf-8",
    )
    archive_path = tmp_path / "bundle.tgz"
    with tarfile.open(archive_path, "w:gz") as tar:
        tar.add(work_dir, arcname=".")
    return archive_path


@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


def test_apply_and_doctor_commands(monkeypatch: pytest.MonkeyPatch, tmp_path: Path, runner: CliRunner) -> None:
    archive = _build_bundle_archive(tmp_path)

    result = runner.invoke(
        app,
        ["apply", "--bundle", str(archive), "--atomic", "--no-browser"],
    )
    assert result.exit_code == 0, result.stdout
    assert "Bundle applied" in result.stdout

    def fake_urlopen(request, timeout=5):  # type: ignore[override]
        class _Response:
            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, tb):
                return False

            def read(self) -> bytes:
                return b'{"status":"ok","details":{"providers":1}}'

        return _Response()

    monkeypatch.setattr("aion.services.doctor.urllib.request.urlopen", fake_urlopen)
    result_doctor = runner.invoke(app, ["doctor", "--verbose"])
    assert result_doctor.exit_code == 0, result_doctor.stdout
    assert "All systems healthy" in result_doctor.stdout
