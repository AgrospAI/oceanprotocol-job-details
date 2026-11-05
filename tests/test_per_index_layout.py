import json

from pathlib import Path

from oceanprotocol_job_details.helpers import load_job_details
from oceanprotocol_job_details.settings import JobSettings


def make_base(tmp_path: Path) -> Path:
    """Create the /data skeleton an Ocean Node job exposes to algorithms."""
    (tmp_path / "inputs").mkdir()
    (tmp_path / "ddos").mkdir()
    (tmp_path / "outputs").mkdir()
    (tmp_path / "inputs" / "algoCustomData.json").write_text(
        json.dumps({"example": "value", "isTrue": True})
    )
    return tmp_path


def load(base: Path, dids: str):
    return load_job_details(
        None,
        {
            "base_dir": str(base),
            "dids": dids,
            "transformation_did": "did:ope:algorithm",
        },
    )


def test_per_index_layout_resolves_inputs_by_position(tmp_path):
    """Ocean Node >= 4.6: DIDS is index-aligned with /data/inputs/<index>."""
    base = make_base(tmp_path)
    (base / "inputs" / "0").mkdir()
    (base / "inputs" / "1").mkdir()
    (base / "inputs" / "0" / "parcels.csv").write_text("parcel")
    (base / "inputs" / "1" / "sigpac.geojson").write_text("{}")
    (base / "ddos" / "did:ope:aaa").write_text("{}")
    (base / "ddos" / "did:ope:bbb").write_text("{}")

    job_details = load(base, '["did:ope:aaa", "did:ope:bbb"]')

    assert [entry.did for entry in job_details.files] == [
        "did:ope:aaa",
        "did:ope:bbb",
    ]
    assert [
        path.parent.name for entry in job_details.files for path in entry.input_files
    ] == [
        "0",
        "1",
    ]
    assert [path.name for entry in job_details.files for path in entry.input_files] == [
        "parcels.csv",
        "sigpac.geojson",
    ]
    assert job_details.files[0].ddo == base / "ddos" / "did:ope:aaa"


def test_per_index_layout_supports_null_did_entries(tmp_path):
    """Free-compute inputs have no DID and are only addressable by their index."""
    base = make_base(tmp_path)
    (base / "inputs" / "0").mkdir()
    (base / "inputs" / "1").mkdir()
    (base / "inputs" / "0" / "raw.csv").write_text("raw")
    (base / "inputs" / "1" / "dataset.csv").write_text("dataset")
    (base / "ddos" / "did:ope:bbb").write_text("{}")

    job_details = load(base, '[null, "did:ope:bbb"]')

    assert [entry.did for entry in job_details.files] == ["0", "did:ope:bbb"]
    assert job_details.files[0].ddo is None
    assert [
        path.parent.name for entry in job_details.files for path in entry.input_files
    ] == [
        "0",
        "1",
    ]


def test_legacy_did_named_layout_still_works(tmp_path):
    """Nodes older than 4.6 write /data/inputs/<did> and must keep working."""
    base = make_base(tmp_path)
    (base / "inputs" / "did:ope:aaa").mkdir()
    (base / "inputs" / "did:ope:aaa" / "data.csv").write_text("legacy")
    (base / "ddos" / "did:ope:aaa").write_text("{}")

    job_details = load(base, '["did:ope:aaa"]')

    assert [entry.did for entry in job_details.files] == ["did:ope:aaa"]
    assert [
        path.parent.name for entry in job_details.files for path in entry.input_files
    ] == ["did:ope:aaa"]


def test_settings_accept_null_dids():
    settings = JobSettings(
        base_dir="./_data",
        dids='[null, "did:ope:bbb"]',
        transformation_did="did:ope:algorithm",
    )

    assert settings.dids == [None, "did:ope:bbb"]
