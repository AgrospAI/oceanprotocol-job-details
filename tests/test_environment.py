import json
from dataclasses import asdict, dataclass
from pathlib import Path

import pytest

from oceanprotocol_job_details.job_details import OceanProtocolJobDetails
from oceanprotocol_job_details.ocean import JobDetails


@dataclass(frozen=True)
class CustomParameters:
    example: str
    isTrue: bool


details: JobDetails[CustomParameters]


@pytest.fixture(scope="session", autouse=True)
def setup():  # type: ignore
    global details

    details = OceanProtocolJobDetails(CustomParameters).load()

    yield

    print("JobDetails", details)
    print("Ending session")


def test_files() -> None:
    assert details.files, "There should be detected files"
    assert len(details.files) == 1, "There should be exactly one detected file"
    for file in details.files:
        assert file.ddo, "There should be a DDO file"
        assert file.input_files
        assert len(file.input_files) == 1, "There should be exactly one detected file"

    assert details.files[0], "Can't access files by index"


def test_ddo() -> None:
    assert details.ddos
    assert len(details.ddos) == 1, "There should be exactly one detected DDO"

    excluded_keys = ["accessDetails"]
    with open(details.files.files[0].ddo) as ddo_file:
        ddo_keys = list(json.loads(ddo_file.read()).keys())
        ddo_keys = [key for key in ddo_keys if key not in excluded_keys]

    loaded_ddo_keys = list(details.ddos[0].to_dict().keys())
    assert ddo_keys == loaded_ddo_keys, "DDO keys mismatch. "


def test_algorithm_custom_parameters() -> None:
    assert details.input_parameters is not None
    assert len(asdict(details.input_parameters).keys()) == 2
    assert details.input_parameters.isTrue
    assert details.input_parameters.isTrue is True
    assert details.input_parameters.example
    assert details.input_parameters.example == "data"


def test_empty_custom_parameters() -> None:
    empty_details = OceanProtocolJobDetails().load()  # type: ignore
    assert (
        len(empty_details.input_parameters.to_dict().keys()) == 0
    ), "There should be no input parameters"


def test_stringified_dict_custom_parameters() -> None:
    # create a temporary parameters file with stringified JSON
    from oceanprotocol_job_details.config import config

    params_file = config.path_algorithm_custom_parameters
    params_file.write_text(
        json.dumps(
            {
                "example": json.dumps("data"),  # stringified primitive
                "isTrue": json.dumps(True),  # stringified boolean
            }
        )
    )

    # Load JobDetails with this custom parameters file
    details = OceanProtocolJobDetails(CustomParameters).load()

    # The stringified JSON should be parsed back into the correct types
    assert details.input_parameters.example == "data"
    assert details.input_parameters.isTrue is True
