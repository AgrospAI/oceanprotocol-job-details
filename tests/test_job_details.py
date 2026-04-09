from unittest.mock import patch

import pytest

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
        mock_read_func.return_value = mock_params

        result = job_details.read()
        assert isinstance(result, ParametrizedJobDetails)
        assert result.input_parameters == mock_params

    @patch("oceanprotocol_job_details.ocean.read_input_parameters")
    def test_read_failure_propagation(self, mock_read_func, job_details):
        cause = RuntimeError("asd")

        inner_error = JobDetailsError("Original Error")
        inner_error.__cause__ = cause
        mock_read_func.return_value = inner_error

        error = job_details.read()
        assert error.__cause__ == cause

    def test_read_no_input_type(self, job_details):
        job_details = job_details.model_copy(update={"input_type": None})

        error = job_details.read()
        assert "no input parameters" in str(error)

    @pytest.mark.asyncio
    @patch("oceanprotocol_job_details.ocean.aread_input_parameters")
    async def test_aread_success(self, mock_aread_func, job_details):
        mock_params = CustomParameters(example="async_test", isTrue=True)
        mock_aread_func.return_value = mock_params

        result = await job_details.aread()
        assert result.input_parameters == mock_params

    @pytest.mark.asyncio
    @patch("oceanprotocol_job_details.ocean.aread_input_parameters")
    async def test_aread_failure_propagation(self, mock_aread_func, job_details):
        cause = RuntimeError("asd")

        inner_error = JobDetailsError("Async Fail")
        inner_error.__cause__ = cause
        mock_aread_func.return_value = inner_error

        error = await job_details.aread()
        assert error.__cause__ == cause

    @pytest.mark.asyncio
    async def test_aread_no_input_type(self, job_details):
        job_details = job_details.model_copy(update={"input_type": None})

        error = await job_details.aread()
        assert "no input parameters" in str(error)


class TestJobDetailsLoaders:
    def test_load_parametrized_job_details_success(self, config):
        job_details = load_parametrized_job_details(CustomParameters, config)
        assert isinstance(job_details, ParametrizedJobDetails)

    @patch(
        "oceanprotocol_job_details.ocean.JobDetails.read",
        return_value=JobDetailsError("Mock Error"),
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
        return_value=JobDetailsError("Mock Error"),
    )
    async def test_aload_parametrized_job_details_failure_propagation(
        self, mock_read, config
    ):
        with pytest.raises(JobDetailsError):
            _ = await aload_parametrized_job_details(CustomParameters, config)
