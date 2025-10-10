import json
import shutil
import tempfile
from dataclasses import asdict, dataclass
from pathlib import Path

import pytest

from oceanprotocol_job_details import JobDetails
from oceanprotocol_job_details.di import Container


@dataclass(frozen=True)
class CustomParameters:
    example: str
    isTrue: bool


@pytest.fixture(scope="session", autouse=True)
def base_dir():
    yield {"base_dir": "./_data"}


@pytest.fixture(scope="session", autouse=True)
def config(base_dir):
    yield {
        **base_dir,
        "dids": '["17feb697190d9f5912e064307006c06019c766d35e4e3f239ebb69fb71096e42"]',
        "secret": "a super secret secret",
        "transformation_did": "1234567890",
    }


@pytest.fixture(scope="session", autouse=True)
def details(config):
    yield JobDetails.load(
        CustomParameters,
        **config,
    )


@pytest.fixture(scope="session", autouse=True)
def empty_details(config):
    yield JobDetails.load(**config)


@pytest.fixture(scope="session", autouse=True)
def empty_config_details(base_dir):
    yield JobDetails.load(**base_dir)


def test_files(details) -> None:
    assert details.files, "There should be detected files"
    assert len(details.files) == 1, "There should be exactly one detected file"
    for file in details.files:
        assert file.ddo, "There should be a DDO file"
        assert file.input_files
        assert len(file.input_files) == 1, "There should be exactly one detected file"

    assert details.files[0], "Can't access files by index"


def test_ddo(details) -> None:
    assert details.ddos
    assert len(details.ddos) == 1, "There should be exactly one detected DDO"

    excluded_keys = ["accessDetails"]
    with open(details.files.files[0].ddo) as ddo_file:
        ddo_keys = list(json.loads(ddo_file.read()).keys())
        ddo_keys = [key for key in ddo_keys if key not in excluded_keys]

    loaded_ddo_keys = list(details.ddos[0].to_dict().keys())
    assert ddo_keys == loaded_ddo_keys, "DDO keys mismatch. "


def test_algorithm_custom_parameters(details) -> None:
    assert details.input_parameters is not None
    assert len(asdict(details.input_parameters).keys()) == 2
    assert details.input_parameters.isTrue
    assert details.input_parameters.isTrue is True
    assert details.input_parameters.example
    assert details.input_parameters.example == "data"


def test_empty_custom_parameters(empty_details) -> None:
    assert (
        len(empty_details.input_parameters.to_dict().keys()) == 0
    ), "There should be no input parameters"


def test_stringified_dict_custom_parameters(config, empty_details) -> None:
    # create a temporary parameters file with stringified JSON

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)

        # Copy original data to tmp path
        src_data_dir = empty_details.paths._base
        dst_data_dir = tmp_path / "."
        shutil.copytree(src_data_dir, dst_data_dir, dirs_exist_ok=True)

        container = Container()
        container.config.base_dir.from_Value(tmp_path)

        paths = container.paths(base_dir=tmp_dir)
        paths.algorithm_custom_parameters.write_text(
            json.dumps(
                {
                    "example": json.dumps("data"),  # stringified primitive
                    "isTrue": json.dumps(True),  # stringified boolean
                }
            )
        )

        config["base_dir"] = tmp_path
        # Load JobDetails with this custom parameters file
        details = JobDetails[CustomParameters].load(
            _type=CustomParameters,
            **config,
        )

        # The stringified JSON should be parsed back into the correct types
        assert details.input_parameters.example == "data"
        assert details.input_parameters.isTrue is True


def test_yielding_files(details) -> None:
    files = list(details.next_path())

    assert len(files) == 1
    assert isinstance(files[0], tuple)

    idx, path = files[0]
    assert idx == 0
    assert path.exists() and path.is_file()


def test_empty_config_defaults(empty_config_details) -> None:
    assert "17feb697190d9f5912e064307006c06019c766d35e4e3f239ebb69fb71096e42" in [
        f.did for f in empty_config_details.files
    ], "Did not auto-detect DIDS"
