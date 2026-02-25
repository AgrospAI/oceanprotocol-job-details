from unittest.mock import patch

import pytest
from returns.io import IOFailure, IOSuccess
from returns.result import Failure, Success
from typing_extensions import assert_never

from oceanprotocol_job_details import ParametrizedJobDetails
from oceanprotocol_job_details.exceptions import JobDetailsError
from oceanprotocol_job_details.helpers import (
    aload_parametrized_job_details,
    load_empty_job_details,
    load_parametrized_job_details,
)
from oceanprotocol_job_details.ocean import EmptyJobDetails
from tests.data import CustomParameters


class TestJobDetails:
    @patch("oceanprotocol_job_details.ocean.read_input_parameters")
    def test_read_success(self, mock_read_func, job_details):
        mock_params = CustomParameters(example="test", isTrue=True)
        mock_read_func.return_value = Success(mock_params)

        match job_details.read():
            case Success(result):
                assert isinstance(result, ParametrizedJobDetails)
                assert result.input_parameters == mock_params
            case _:
                assert_never()

    @patch("oceanprotocol_job_details.ocean.read_input_parameters")
    def test_read_failure_propagation(self, mock_read_func, job_details):
        cause = RuntimeError("asd")

        inner_error = JobDetailsError("Original Error")
        inner_error.__cause__ = cause
        mock_read_func.return_value = Failure(inner_error)

        match job_details.read():
            case Failure(error):
                assert error.__cause__ == cause
            case _:
                assert_never()

    def test_read_no_input_type(self, job_details):
        job_details = job_details.model_copy(update={"input_type": None})

        match job_details.read():
            case Failure(error):
                assert "no input parameters" in str(error)
            case _:
                assert_never()

    @pytest.mark.asyncio
    @patch("oceanprotocol_job_details.ocean.aread_input_parameters")
    async def test_aread_success(self, mock_aread_func, job_details):
        mock_params = CustomParameters(example="async_test", isTrue=True)
        mock_aread_func.return_value = IOSuccess(mock_params)

        match await job_details.aread():
            case IOSuccess(Success(result)):
                assert result.input_parameters == mock_params
            case _:
                assert_never()

    @pytest.mark.asyncio
    @patch("oceanprotocol_job_details.ocean.aread_input_parameters")
    async def test_aread_failure_propagation(self, mock_aread_func, job_details):
        cause = RuntimeError("asd")

        inner_error = JobDetailsError("Async Fail")
        inner_error.__cause__ = cause
        mock_aread_func.return_value = IOFailure(inner_error)

        match await job_details.aread():
            case IOFailure(Failure(error)):
                assert error.__cause__ == cause
            case _:
                assert_never()

    @pytest.mark.asyncio
    async def test_aread_no_input_type(self, job_details):
        job_details = job_details.model_copy(update={"input_type": None})

        match await job_details.aread():
            case IOFailure(Failure(error)):
                assert "no input parameters" in str(error)
            case _:
                assert_never()


class TestJobDetailsLoaders:
    def test_load_parametrized_job_details_success(self, config):
        job_details = load_parametrized_job_details(CustomParameters, config)
        assert isinstance(job_details, ParametrizedJobDetails)

    @patch(
        "oceanprotocol_job_details.ocean.JobDetails.read",
        return_value=Failure(JobDetailsError("Mock Error")),
    )
    def test_load_parametrized_job_details_failure_propagation(self, mock_read, config):
        with pytest.raises(JobDetailsError):
            _ = load_parametrized_job_details(CustomParameters, config)

    def test_load_empty_job_details(self, config):
        job_details = load_empty_job_details(config)
        assert isinstance(job_details, EmptyJobDetails)

    @pytest.mark.asyncio
    async def test_aload_parametrized_job_details_success(self, config):
        job_details = await aload_parametrized_job_details(CustomParameters, config)
        assert isinstance(job_details, ParametrizedJobDetails)

    @pytest.mark.asyncio
    @patch(
        "oceanprotocol_job_details.ocean.JobDetails.aread",
        return_value=IOFailure(JobDetailsError("Mock Error")),
    )
    async def test_aload_parametrized_job_details_failure_propagation(
        self, mock_read, config
    ):
        with pytest.raises(JobDetailsError):
            _ = await aload_parametrized_job_details(CustomParameters, config)
