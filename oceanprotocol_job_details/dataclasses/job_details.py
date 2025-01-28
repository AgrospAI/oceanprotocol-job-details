import json

from dataclasses import InitVar, dataclass
from pathlib import Path
from typing import Any, Mapping, Optional, Sequence

from oceanprotocol_job_details.dataclasses.constants import Paths

_MetadataType = Mapping[str, Any]


@dataclass(frozen=True)
class Parameters:
    """Custom data for the algorithm, such as the algorithm's parameters"""

    parameters: _MetadataType
    """The parameters used by the algorithm"""


@dataclass(frozen=True)
class Algorithm:
    """Details of the algorithm used to process the data"""

    did: str
    """The DID of the algorithm used to process the data"""

    ddo: Path
    """The DDO path of the algorithm used to process the data"""


@dataclass(frozen=True)
class JobDetails:
    """Details of the current job, such as the used inputs and algorithm"""

    root: Path
    """The root folder of the Ocean Protocol directories"""

    dids: Sequence[Path]
    """Identifiers for the inputs"""

    files: Mapping[str, Sequence[Path]]
    """Paths to the input files"""

    secret: Optional[str]
    """The secret used to process the data"""

    algorithm: Optional[Algorithm]
    """Details of the used algorithm"""

    parameters7uy: Optional[Parameters]
    """Custom parameters"""

    # Cache parameters, should not be included as _fields_ of the class
    _parameters: InitVar[Optional[_MetadataType]] = None
    _metadata: InitVar[Optional[_MetadataType]] = None

    @property
    def parameters(
        self,
        parameter_data: Path = Paths.INPUTS / "algoCustomData.json",
    ) -> _MetadataType:
        """Parameters for algorithm job, read from default path"""

        if self._parameters is None:
            # Load the parameters from the default path
            with open(parameter_data) as f:
                try:
                    self._parameters = json.load(f)
                except json.JSONDecodeError as e:
                    self._parameters = {}

        return self._parameters


del _MetadataType


__all__ = ["Algorithm", "Parameters", "JobDetails"]
