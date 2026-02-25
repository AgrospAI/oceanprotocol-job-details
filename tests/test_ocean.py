import json
from typing import assert_never
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pydantic import ValidationError
from returns.io import IOFailure, IOSuccess
from returns.result import Failure, Success

from oceanprotocol_job_details.exceptions import JobDetailsError
from oceanprotocol_job_details.ocean import (
    aread_input_parameters,
    read_input_parameters,
)
from tests.data import CustomParameters


class TestReadInputParameters:
    @patch("pathlib.Path.exists", return_value=False)
    def test_file_missing_returns_failure(self, mock_exists):
        mock_paths = MagicMock()
        mock_paths.algorithm_custom_parameters.exists.return_value = False

        match read_input_parameters(mock_paths, CustomParameters):
            case Failure(error):
                assert "missing" in str(error)
            case _:
                assert_never()

    @patch("pathlib.Path.exists", return_value=True)
    @patch("pathlib.Path.read_text", return_value="")
    def test_empty_file_returns_failure(self, mock_read, mock_exists):
        mock_paths = MagicMock()
        mock_paths.algorithm_custom_parameters.read_text.return_value = ""

        match read_input_parameters(mock_paths, CustomParameters):
            case Failure(error):
                assert "empty" in str(error)
            case _:
                assert_never()

    def test_invalid_json_returns_validation_error(self):
        mock_paths = MagicMock()
        mock_paths.algorithm_custom_parameters.exists.return_value = True
        mock_paths.algorithm_custom_parameters.read_text.return_value = (
            '{"name": "test"}'
        )

        match read_input_parameters(mock_paths, CustomParameters):
            case Failure(error):
                assert isinstance(error, JobDetailsError)
                assert isinstance(error.__cause__, ValidationError)
            case _:
                assert_never()

    def test_valid_input_returns_success(self):
        mock_paths = MagicMock()
        mock_paths.algorithm_custom_parameters.exists.return_value = True
        mock_paths.algorithm_custom_parameters.read_text.return_value = (
            '{"example": "data", "isTrue": true}'
        )

        match read_input_parameters(mock_paths, CustomParameters):
            case Success(result):
                assert result.example == "data"
                assert result.isTrue
            case _:
                assert_never()


class TestAReadInputParameters:
    @pytest.mark.asyncio
    @patch("pathlib.Path.exists", return_value=False)
    async def test_file_missing_returns_failure(self, mock_exists):
        mock_paths = MagicMock()
        mock_paths.algorithm_custom_parameters.exists.return_value = False

        match await aread_input_parameters(mock_paths, CustomParameters):
            case IOFailure(Failure(error)):
                assert "missing" in str(error)
            case _:
                assert_never()

    @pytest.mark.asyncio
    @patch("pathlib.Path.exists", return_value=True)
    @patch("aiofiles.open")
    async def test_empty_file_returns_failure(self, mock_open, mock_exists):
        mock_file = AsyncMock()
        mock_file.read.return_value = ""

        mock_open.return_value.__aenter__.return_value = mock_file

        mock_paths = MagicMock()

        match await aread_input_parameters(mock_paths, CustomParameters):
            case IOFailure(Failure(error)):
                assert "empty" in str(error)
            case _:
                assert_never()

    @pytest.mark.asyncio
    @patch("aiofiles.open")
    async def test_invalid_json_returns_validation_error(self, mock_open):
        mock_file = AsyncMock()
        mock_file.read.return_value = '{"foo": "bar"}'

        mock_open.return_value.__aenter__.return_value = mock_file

        mock_paths = MagicMock()

        match await aread_input_parameters(mock_paths, CustomParameters):
            case IOFailure(Failure(error)):
                assert isinstance(error, JobDetailsError)
                assert isinstance(error.__cause__, ValidationError)
            case _:
                assert_never()

    @pytest.mark.asyncio
    @patch("aiofiles.open")
    async def test_valid_input_returns_success(self, mock_open):
        mock_file = AsyncMock()
        mock_file.read.return_value = '{"example": "data", "isTrue": true}'

        mock_open.return_value.__aenter__.return_value = mock_file

        mock_paths = MagicMock()

        match await aread_input_parameters(mock_paths, CustomParameters):
            case IOSuccess(Success(result)):
                assert result.example == "data"
                assert result.isTrue
            case _:
                assert_never()

    def test_stringified_dict_custom_parameters_logic(job_details):
        """
        Instead of tempfiles, we mock the 'read_text' to return stringified JSON
        to verify Pydantic/logic handles it.
        """
        mock_paths = MagicMock()
        mock_paths.algorithm_custom_parameters.exists.return_value = True
        # Mimicking the complex stringified format from your previous test
        mock_paths.algorithm_custom_parameters.read_text.return_value = json.dumps(
            {"example": "data", "isTrue": True}
        )

        match read_input_parameters(mock_paths, CustomParameters):
            case Success(result):
                assert result.example == "data"
                assert result.isTrue
