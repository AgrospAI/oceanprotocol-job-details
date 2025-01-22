from dataclasses import dataclass
from enum import Enum
from pathlib import Path


@dataclass(frozen=True, slots=True)
class EnvironmentKeys:
    """Environment keys passed to the algorithm"""

    ROOT: str = "ROOT_FOLDER"
    SECRET: str = "secret"
    ALGORITHM: str = "TRANSFORMATION_DID"
    DIDS: str = "DIDS"


@dataclass(frozen=True, slots=True)
class DidKeys:
    SERVICE: str = "service"
    SERVICE_TYPE: str = "type"
    ATTRIBUTES: str = "attributes"
    MAIN: str = "main"
    FILES: str = "files"


class ServiceType(Enum):
    METADATA: str = "metadata"


@dataclass(frozen=True, slots=True)
class Paths:
    DATA: Path = Path("data")
    INPUTS: Path = DATA / "inputs"
    DDOS: Path = DATA / "ddos"
    OUTPUTS: Path = DATA / "outputs"
    LOGS: Path = DATA / "logs"
    