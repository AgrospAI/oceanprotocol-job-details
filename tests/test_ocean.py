import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pydantic import ValidationError

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

        error = read_input_parameters(mock_paths, CustomParameters)
        assert isinstance(error, JobDetailsError)
        assert "missing" in str(error)

    @patch("pathlib.Path.exists", return_value=True)
    @patch("pathlib.Path.read_text", return_value="")
    def test_empty_file_returns_failure(self, mock_read, mock_exists):
        mock_paths = MagicMock()
        mock_paths.algorithm_custom_parameters.read_text.return_value = ""

        error = read_input_parameters(mock_paths, CustomParameters)
        assert isinstance(error, JobDetailsError)
        assert "empty" in str(error)

    def test_invalid_json_returns_validation_error(self):
        mock_paths = MagicMock()
        mock_paths.algorithm_custom_parameters.exists.return_value = True
        mock_paths.algorithm_custom_parameters.read_text.return_value = (
            '{"name": "test"}'
        )

        error = read_input_parameters(mock_paths, CustomParameters)
        assert isinstance(error, JobDetailsError)
        assert isinstance(error.__cause__, ValidationError)

    def test_valid_input_returns_success(self):
        mock_paths = MagicMock()
        mock_paths.algorithm_custom_parameters.exists.return_value = True
        mock_paths.algorithm_custom_parameters.read_text.return_value = (
            '{"example": "data", "isTrue": true}'
        )

        result = read_input_parameters(mock_paths, CustomParameters)
        assert isinstance(result, CustomParameters)
        assert result.example == "data"
        assert result.isTrue


class TestAReadInputParameters:
    @pytest.mark.asyncio
    @patch("pathlib.Path.exists", return_value=False)
    async def test_file_missing_returns_failure(self, mock_exists):
        mock_paths = MagicMock()
        mock_paths.algorithm_custom_parameters.exists.return_value = False

        error = await aread_input_parameters(mock_paths, CustomParameters)
        assert isinstance(error, JobDetailsError)
        assert "missing" in str(error)

    @pytest.mark.asyncio
    @patch("pathlib.Path.exists", return_value=True)
    @patch("aiofiles.open")
    async def test_empty_file_returns_failure(self, mock_open, mock_exists):
        mock_file = AsyncMock()
        mock_file.read.return_value = ""

        mock_open.return_value.__aenter__.return_value = mock_file

        mock_paths = MagicMock()

        error = await aread_input_parameters(mock_paths, CustomParameters)
        assert isinstance(error, JobDetailsError)
        assert "empty" in str(error)

    @pytest.mark.asyncio
    @patch("aiofiles.open")
    async def test_invalid_json_returns_validation_error(self, mock_open):
        mock_file = AsyncMock()
        mock_file.read.return_value = '{"foo": "bar"}'

        mock_open.return_value.__aenter__.return_value = mock_file

        mock_paths = MagicMock()

        error = await aread_input_parameters(mock_paths, CustomParameters)
        assert isinstance(error, JobDetailsError)
        assert isinstance(error.__cause__, ValidationError)

    @pytest.mark.asyncio
    @patch("aiofiles.open")
    async def test_valid_input_returns_success(self, mock_open):
        mock_file = AsyncMock()
        mock_file.read.return_value = '{"example": "data", "isTrue": true}'

        mock_open.return_value.__aenter__.return_value = mock_file

        mock_paths = MagicMock()

        result = await aread_input_parameters(mock_paths, CustomParameters)
        assert isinstance(result, CustomParameters)
        assert result.example == "data"
        assert result.isTrue

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

        result = read_input_parameters(mock_paths, CustomParameters)
        assert isinstance(result, CustomParameters)
        assert result.example == "data"
        assert result.isTrue
