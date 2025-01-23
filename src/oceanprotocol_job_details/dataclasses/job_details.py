from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Optional, Sequence


@dataclass(frozen=True)
class Algorithm:
    did: str
    """The DID of the algorithm used to process the data"""

    ddo: Path
    """The DDO path of the algorithm used to process the data"""


@dataclass(frozen=True)
class JobDetails:
    """Details of the current job, such as the used inputs and algorithm"""

    root: Path
    """The root folder of the Ocean Protocol directories"""

    dids: Optional[Sequence[Path]]
    """Identifiers for the inputs"""

    metadata: Mapping[str, Any]
    """TODO: To define"""

    files: Mapping[str, Sequence[Path]]
    """Paths to the input files"""

    secret: Optional[str]
    """The secret used to process the data"""

    algorithm: Optional[Algorithm]
    """Details of the used algorithm"""
