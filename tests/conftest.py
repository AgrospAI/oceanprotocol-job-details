import pytest

from oceanprotocol_job_details import (
    load_empty_job_details,
    load_parametrized_job_details,
)
from oceanprotocol_job_details.helpers import load_job_details
from oceanprotocol_job_details.settings import JobSettings
from tests.data import CustomParameters


@pytest.fixture(scope="function")
def config():
    yield {
        "base_dir": "./_data",
        "dids": '["17feb697190d9f5912e064307006c06019c766d35e4e3f239ebb69fb71096e42"]',
        "secret": "a super secret secret",
        "transformation_did": "1234567890",
    }


@pytest.fixture(scope="function")
def settings(config):
    yield JobSettings(**config)


@pytest.fixture(scope="function")
def job_details(config):
    yield load_job_details(CustomParameters, config)


@pytest.fixture(scope="function")
def parametrized_job_details(config):
    yield load_parametrized_job_details(CustomParameters, config)


@pytest.fixture(scope="function")
def empty_job_details(config):
    yield load_empty_job_details(config)
