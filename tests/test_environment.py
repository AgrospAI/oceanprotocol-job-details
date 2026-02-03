import json
import shutil
import tempfile
from pathlib import Path
from typing import Generator

import aiofiles
import orjson
import pytest
from pydantic import BaseModel

from oceanprotocol_job_details import JobDetails
from oceanprotocol_job_details.helpers import create_container, load_job_details


class CustomParameters(BaseModel):
    example: str
    isTrue: bool


@pytest.fixture(scope="session")
def config():
    yield {
        "base_dir": "./_data",
        "dids": '["17feb697190d9f5912e064307006c06019c766d35e4e3f239ebb69fb71096e42"]',
        "secret": "a super secret secret",
        "transformation_did": "1234567890",
    }


@pytest.fixture(scope="session")
def job_details(config) -> Generator[JobDetails[CustomParameters], None, None]:
    yield load_job_details(config, CustomParameters)


@pytest.fixture(scope="session")
def empty_job_details(config) -> Generator[JobDetails[None], None, None]:
    yield load_job_details(config)


def test_minimal_config():
    assert load_job_details({"base_dir": "./_data", "transformation_did": "1234567890"})


def test_files(job_details):
    assert job_details.files, "There should be detected files"
    assert len(job_details.files) == 1, "There should be exactly one detected file"
    for file in job_details.files:
        assert file.ddo, "There should be a DDO file"
        assert file.input_files
        assert len(file.input_files) == 1, "There should be exactly one detected file"

    assert job_details.files[0], "Can't access files by index"

    outputs = job_details.paths.outputs.glob("*")
    logs = job_details.paths.logs.glob("*")

    assert len(list(outputs)) == 0
    assert len(list(logs)) == 1, "There should be one log"


def test_empty_dids(config):
    config = config.copy()
    config.pop("dids")

    job_details = load_job_details(config)
    files = list(job_details.inputs())
    assert len(files) == 1


@pytest.mark.asyncio
async def test_ddo(job_details):
    ddo = job_details.metadata.items()

    assert len(ddo) == 1, "There should be exactly one detected DDO"

    excluded_keys = ["accessDetails"]

    for f in job_details.files:
        async with aiofiles.open(f.ddo, "r") as ddo_file:
            ddo_keys = list(orjson.loads(await ddo_file.read()).keys())
            ddo_keys = [key for key in ddo_keys if key not in excluded_keys]

            loaded_ddo_keys = list(
                job_details.metadata[f.did].model_dump(by_alias=True).keys()
            )
            assert ddo_keys == loaded_ddo_keys, "DDO keys mismatch"


@pytest.mark.asyncio
async def test_algorithm_custom_parameters(job_details):
    parameters = await job_details.input_parameters()
    assert parameters is not None
    assert len(parameters.model_dump().keys()) == 2
    assert parameters.isTrue
    assert parameters.isTrue is True
    assert parameters.example
    assert parameters.example == "data"


@pytest.mark.asyncio
async def test_empty_custom_parameters(empty_job_details):
    parameters = await empty_job_details.input_parameters()
    assert parameters is None, "Input Parameters should be None"


@pytest.mark.asyncio
async def test_stringified_dict_custom_parameters(config):
    # Create a temporary directory to hold custom parameter file
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)

        # Copy original JobDetails data to the temp directory
        original_base = Path(config["base_dir"])
        shutil.copytree(original_base, tmp_path, dirs_exist_ok=True)

        # Reconfigure container to use the temp directory
        container = create_container({**config, "base_dir": tmp_path})

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

        details = load_job_details(config, CustomParameters)

        # Ensure stringified JSON is parsed correctly

        parameters = await details.input_parameters()
        assert parameters.example == "data"
        assert parameters.isTrue is True


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
