from pathlib import Path
from unittest.mock import patch

import pytest

from oceanprotocol_job_details.domain.derived import DIDPaths, Paths


class TestDerived:
    @patch("pathlib.Path.exists", return_value=False)
    def test_did_paths_throws(self, mock_exists):
        with pytest.raises(FileNotFoundError):
            DIDPaths("", Path())

    @patch("pathlib.Path.exists", return_value=True)
    def test_did_paths_length(self, mock_exists):
        paths = DIDPaths("", Path(), input_files=[""] * 67)

        assert len(paths) == 67

    def test_paths(self):
        base = Path("/data")
        paths = Paths(base)

        assert paths.base_dir == paths.data == base
        assert paths.ddos == base / "ddos"
        assert paths.inputs == base / "inputs"
        assert paths.outputs == base / "outputs"
        assert paths.logs == base / "logs"
        assert (
            paths.algorithm_custom_parameters == base / "inputs" / "algoCustomData.json"
        )
