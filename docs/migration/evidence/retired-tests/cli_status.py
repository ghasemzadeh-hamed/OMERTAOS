from cli import main as cli_main


def test_status_missing_artifact(tmp_path):
    code = cli_main.main(["status", "--artifacts", str(tmp_path / "missing.json")])
    assert code == 1
