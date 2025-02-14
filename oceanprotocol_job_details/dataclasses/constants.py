from dataclasses import dataclass
from pathlib import Path


@dataclass(
    frozen=True,
)
class _DidKeys:
    """Common keys inside the DIDs"""

    SERVICE: str = "service"
    SERVICE_TYPE: str = "type"
    ATTRIBUTES: str = "attributes"
    MAIN: str = "main"
    FILES: str = "files"


@dataclass(
    frozen=True,
)
class _ServiceType:
    """Service types inside the DIDs"""

    METADATA: str = "metadata"


@dataclass()
class _Paths:
    """Common paths used in the Ocean Protocol directories"""

    DATA: Path = Path("/data")

    INPUTS: Path = DATA / "inputs"
    DDOS: Path = DATA / "ddos"
    OUTPUTS: Path = DATA / "outputs"
    LOGS: Path = DATA / "logs"

    ALGORITHM_CUSTOM_PARAMETERS: Path = INPUTS / "algoCustomData.json"


DidKeys = _DidKeys()
ServiceType = _ServiceType()
Paths = _Paths()

del _DidKeys, _ServiceType, _Paths
