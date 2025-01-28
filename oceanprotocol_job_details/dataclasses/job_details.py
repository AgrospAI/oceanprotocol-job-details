import json
from dataclasses import InitVar, dataclass
from logging import getLogger
from pathlib import Path
from typing import Any, Mapping, Optional, Sequence

from oceanprotocol_job_details.dataclasses.constants import Paths

_MetadataType = Mapping[str, Any]

logger = getLogger(__name__)


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


@dataclass
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

    metadata: Optional[_MetadataType] = None
    """Metadata of the job, TODO"""

    # Cache parameters, should not be included as _fields_ of the class
    _parameters: InitVar[Optional[_MetadataType]] = None

    @property
    def parameters(
        self,
        parameters: Optional[Path] = None,
    ) -> _MetadataType:
        """Parameters for algorithm job, read from default path"""

        if parameters is None:
            parameters = self.root / Paths.ALGORITHM_CUSTOM_PARAMETERS

        if self._parameters is None:
            # Load the parameters from filesystem
            with open(parameters, "r") as f:
                try:
                    self._parameters = json.load(f)
                except json.JSONDecodeError as e:
                    logger.warning(f"Error loading parameters file {parameters}: {e}")
                    self._parameters = {}

        return self._parameters


del _MetadataType


__all__ = ["Algorithm", "Parameters", "JobDetails"]
