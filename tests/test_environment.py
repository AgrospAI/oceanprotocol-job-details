from pathlib import Path

import pytest

from oceanprotocol_job_details.dataclasses.job_details import JobDetails
from oceanprotocol_job_details.dataclasses.constants import Paths
from oceanprotocol_job_details.job_details import OceanProtocolJobDetails
from oceanprotocol_job_details.loaders.impl.map import Keys


details: JobDetails = None


@pytest.fixture(scope="session", autouse=True)
def setup():
    keys = Keys()

    fake_env = {
        keys.DIDS: ' [ "8f67E08be5dD941a701c2491E814535522c33bC2" ]',
        keys.ALGORITHM: "6EDaE15f7314dC306BB6C382517D374356E6B9De",
        keys.SECRET: "MOCK-SECRET",
        keys.ROOT: Path(__file__).parent,
    }

    global details

    details = OceanProtocolJobDetails(
        implementation="map",
        mapper=fake_env,
        keys=keys,
    ).load()

    yield

    print("JobDetails", details)
    print("Ending session")


def test_root():
    assert details.root == Path(__file__).parent, "Incorrect root folder"


def test_files_exists():
    assert details.files, "There should be detected files"


def test_files_len_eq_one():
    assert len(details.files.keys()) == 1, "There should be exactly one detected file"


def test_secret():
    assert details.secret == "MOCK-SECRET", "Incorrect secret"


def test_algorithm_exists():
    assert details.algorithm, "There should be an input algorithm"


def test_algorithm_did():
    assert details.algorithm.did == "6EDaE15f7314dC306BB6C382517D374356E6B9De"


def test_algorithm_ddo():
    assert details.algorithm.ddo == details.root / Paths.DDOS / details.algorithm.did


def test_custom_parameters():
    assert details.parameters is not None
    assert len(details.parameters.keys()) == 2
    assert details.parameters["isTrue"] == True
