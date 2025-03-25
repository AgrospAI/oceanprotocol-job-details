from dataclasses import asdict, dataclass
import os

import pytest

from oceanprotocol_job_details.job_details import OceanProtocolJobDetails
from oceanprotocol_job_details.ocean import JobDetails


@dataclass(frozen=True)
class CustomParameters:
    isTrue: bool


details: JobDetails[CustomParameters]


@pytest.fixture(scope="session", autouse=True)
def setup():  # type: ignore

    env = os.environ
    env["DIDS"] = (
        ' [ "eb60f87363a36a5ae5cb8373524a8fd976b0cc5f8c40a706c615b857ae0e2974" ]'
    )
    env["TRANSFORMATION_DID"] = "6EDaE15f7314dC306BB6C382517D374356E6B9De"
    env["SECRET"] = "MOCK-SECRET"

    global details

    details = OceanProtocolJobDetails().load()

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


def test_agorithm_custom_parameters() -> None:
    assert details.input_parameters is not None
    assert len(asdict(details.input_parameters).keys()) == 2
    assert details.input_parameters.isTrue
    assert details.input_parameters.isTrue is True
