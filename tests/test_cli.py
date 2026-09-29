import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_cli_compile_and_inspect(tmp_path):
    output = tmp_path / "schematic.json"
    subprocess.run([
        sys.executable, "-m", "nise.cli", "compile",
        str(ROOT / "examples" / "bearing_catalog.json"),
        str(ROOT / "examples" / "bearing_query.json"),
        "--output", str(output),
    ], check=True, cwd=tmp_path)
    value = json.loads(output.read_text())
    assert value["schema"] == "nise.inference-schematic.v1"
    result = subprocess.check_output([
        sys.executable, "-m", "nise.cli", "inspect", str(output)
    ], text=True, cwd=tmp_path)
    inspection = json.loads(result)
    assert inspection["candidate_structure"] is True


def test_cli_refuses_overwrite(tmp_path):
    output = tmp_path / "schematic.json"
    output.write_text("{}")
    completed = subprocess.run([
        sys.executable, "-m", "nise.cli", "compile",
        str(ROOT / "examples" / "bearing_catalog.json"),
        str(ROOT / "examples" / "bearing_query.json"),
        "--output", str(output),
    ], text=True, capture_output=True, cwd=tmp_path)
    assert completed.returncode == 1
    assert json.loads(completed.stderr)["status"] == "refused"
