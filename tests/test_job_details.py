import os
from pathlib import Path

import pytest

from src.oceanprotocol_job_details.job_details import EnvironmentKeys, JobDetails, Paths

details = None


@pytest.fixture(scope="session", autouse=True)
def setup():
    fake_env = {
        EnvironmentKeys.DIDS: ' [ "8f67E08be5dD941a701c2491E814535522c33bC2" ]',
        EnvironmentKeys.ALGORITHM: "6EDaE15f7314dC306BB6C382517D374356E6B9De",
        EnvironmentKeys.SECRET: "MOCK-SECRET",
        EnvironmentKeys.ROOT: Path(__file__).parent,
    }

    global details
    details = JobDetails.from_environment(fake_env)
    yield
    print("JobDetails", details)
    print("Ending session")


def test_root():
    assert details.ROOT == Path(__file__).parent, "Incorrect root folder"


def test_files_exists():
    assert details.FILES, "There should be detected files"


def test_files_len_eq_one():
    assert len(details.FILES.keys()) == 1, "There should be exactly one detected file"


def test_secret():
    assert details.SECRET == "MOCK-SECRET", "Incorrect secret"


def test_algorithm_exists():
    assert details.ALGORITHM, "There should be an input algorithm"


def test_algorithm_did():
    assert details.ALGORITHM.DID == "6EDaE15f7314dC306BB6C382517D374356E6B9De"


def test_algorithm_ddo():
    assert details.ALGORITHM.DDO == details.ROOT / Paths.DDOS / details.ALGORITHM.DID
