import json
import shutil
import tempfile
from pathlib import Path
from typing import Generator

import pytest
from pydantic import BaseModel

from oceanprotocol_job_details import JobDetails
from oceanprotocol_job_details.di import Container
from oceanprotocol_job_details.settings import JobSettings


class CustomParameters(BaseModel):
    example: str
    isTrue: bool


class EmptyParameters(BaseModel): ...


@pytest.fixture(scope="session")
def config():
    yield {
        "base_dir": "./_data",
        "dids": '["17feb697190d9f5912e064307006c06019c766d35e4e3f239ebb69fb71096e42"]',
        "secret": "a super secret secret",
        "transformation_did": "1234567890",
    }


@pytest.fixture(scope="session")
def container():
    def _container(config):
        container = Container()
        settings = JobSettings(**config)
        container.config.from_pydantic(settings)
        return container

    yield _container


@pytest.fixture(scope="session")
def job_details_loader(config, container):
    def _container(input_type):
        return container(config).job_details_loader(input_type=input_type).load()

    yield _container


@pytest.fixture(scope="session")
def job_details(
    job_details_loader,
) -> Generator[JobDetails[CustomParameters], None, None]:
    yield job_details_loader(CustomParameters)


@pytest.fixture(scope="session")
def empty_job_details(
    job_details_loader,
) -> Generator[JobDetails[EmptyParameters], None, None]:
    yield job_details_loader(EmptyParameters)


def test_files(job_details):
    assert job_details.files, "There should be detected files"
    assert len(job_details.files) == 1, "There should be exactly one detected file"
    for file in job_details.files:
        assert file.ddo, "There should be a DDO file"
        assert file.input_files
        assert len(file.input_files) == 1, "There should be exactly one detected file"

    assert job_details.files[0], "Can't access files by index"


def test_ddo(job_details):
    assert job_details.ddos
    assert len(job_details.ddos) == 1, "There should be exactly one detected DDO"

    excluded_keys = ["accessDetails"]
    with open(job_details.files[0].ddo) as ddo_file:
        ddo_keys = list(json.loads(ddo_file.read()).keys())
        ddo_keys = [key for key in ddo_keys if key not in excluded_keys]

    loaded_ddo_keys = list(job_details.ddos[0].model_dump(by_alias=True).keys())
    assert ddo_keys == loaded_ddo_keys, "DDO keys mismatch. "


def test_algorithm_custom_parameters(job_details):
    assert job_details.input_parameters is not None
    assert len(job_details.input_parameters.model_dump().keys()) == 2
    assert job_details.input_parameters.isTrue
    assert job_details.input_parameters.isTrue is True
    assert job_details.input_parameters.example
    assert job_details.input_parameters.example == "data"


def test_empty_custom_parameters(empty_job_details):
    custom_input_keys = empty_job_details.input_parameters.model_dump().keys()
    assert len(custom_input_keys) == 0, "There should be no input parameters"


def test_stringified_dict_custom_parameters(job_details_loader, container, config):
    # Create a temporary directory to hold custom parameter file
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)

        # Copy original JobDetails data to the temp directory
        original_base = Path(config["base_dir"])
        shutil.copytree(original_base, tmp_path, dirs_exist_ok=True)

        # Reconfigure container to use the temp directory
        container = container({**config, "base_dir": tmp_path})

        # Write a stringified JSON parameters file
        paths = container.paths(base_dir=tmp_path)
        paths.algorithm_custom_parameters.write_text(
            json.dumps(
                {
                    "example": json.dumps("data"),  # stringified string
                    "isTrue": json.dumps(True),  # stringified boolean
                }
            )
        )

        details = job_details_loader(CustomParameters)

        # Ensure stringified JSON is parsed correctly
        assert details.input_parameters.example == "data"
        assert details.input_parameters.isTrue is True


def test_yielding_files(job_details):
    files = list(job_details.inputs())

    assert len(files) == 1
    assert isinstance(files[0], tuple)

    idx, path = files[0]
    assert idx == 0
    assert path.exists() and path.is_file()


def test_empty_config_defaults(empty_job_details):
    assert "17feb697190d9f5912e064307006c06019c766d35e4e3f239ebb69fb71096e42" in [
        f.did for f in empty_job_details.files
    ], "Did not auto-detect DIDS"
