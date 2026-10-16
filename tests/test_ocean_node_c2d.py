import json
import tempfile
from pathlib import Path

from oceanprotocol_job_details.helpers import load_job_details
from oceanprotocol_job_details.settings import JobSettings


def test_ocean_node_42_layout():
    """Verify that flat /data/inputs layout without DDOs or DIDS env loads correctly."""
    with tempfile.TemporaryDirectory() as tmpdir:
        base = Path(tmpdir)
        inputs_dir = base / "inputs"
        ddos_dir = base / "ddos"
        outputs_dir = base / "outputs"
        inputs_dir.mkdir()
        ddos_dir.mkdir()  # empty ddos directory as created by Ocean Node 4.2
        outputs_dir.mkdir()

        # Flat input file
        input_file = inputs_dir / "sample_dataset.json"
        input_file.write_text(json.dumps({"key": "value"}))

        config = {
            "base_dir": str(base),
            "transformation_did": "DEFAULT",
        }

        # 1. JobSettings should discover input files from inputs/
        settings = JobSettings(**config)
        assert len(settings.dids) == 1
        assert settings.dids[0] == "sample_dataset.json"

        # 2. load_job_details should succeed without error
        jd = load_job_details(None, config)
        assert len(jd.files) == 1
        assert jd.files[0].did == "sample_dataset.json"
        assert len(jd.files[0].input_files) == 1
        assert jd.files[0].input_files[0] == input_file

        # 3. inputs() iterator should yield (did, path)
        inputs = list(jd.inputs())
        assert len(inputs) == 1
        did, path = inputs[0]
        assert did == "sample_dataset.json"
        assert path == input_file
        assert json.loads(path.read_text()) == {"key": "value"}

        # 4. metadata should have a fallback DDO so metadata is non-empty
        assert len(jd.metadata) == 1
        assert "sample_dataset.json" in jd.metadata
        assert jd.metadata["sample_dataset.json"].id == "sample_dataset.json"


def test_ocean_node_42_multiple_inputs_and_custom_data():
    """Verify multiple inputs while ignoring algoCustomData.json."""
    with tempfile.TemporaryDirectory() as tmpdir:
        base = Path(tmpdir)
        inputs_dir = base / "inputs"
        ddos_dir = base / "ddos"
        inputs_dir.mkdir()
        ddos_dir.mkdir()

        (inputs_dir / "file1.csv").write_text("a,b,c")
        (inputs_dir / "file2.json").write_text("{}")
        (inputs_dir / "algoCustomData.json").write_text(json.dumps({"param": "val"}))

        config = {
            "base_dir": str(base),
            "transformation_did": "DEFAULT",
        }

        settings = JobSettings(**config)
        assert len(settings.dids) == 2
        assert "algoCustomData.json" not in settings.dids
        assert set(settings.dids) == {"file1.csv", "file2.json"}

        jd = load_job_details(None, config)
        inputs = list(jd.inputs())
        assert len(inputs) == 2
        dids = {item[0] for item in inputs}
        assert dids == {"file1.csv", "file2.json"}
