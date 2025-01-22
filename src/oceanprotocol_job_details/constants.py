from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class _EnvironmentKeys:
    """Environment keys passed to the algorithm"""

    ROOT: str = "ROOT_FOLDER"
    SECRET: str = "secret"
    ALGORITHM: str = "TRANSFORMATION_DID"
    DIDS: str = "DIDS"


@dataclass(frozen=True, slots=True)
class _DidKeys:
    """Common keys inside the DIDs"""

    SERVICE: str = "service"
    SERVICE_TYPE: str = "type"
    ATTRIBUTES: str = "attributes"
    MAIN: str = "main"
    FILES: str = "files"


@dataclass(frozen=True, slots=True)
class _ServiceType:
    METADATA: str = "metadata"


@dataclass(frozen=True, slots=True)
class _Paths:
    DATA: Path = Path("data")
    INPUTS: Path = DATA / "inputs"
    DDOS: Path = DATA / "ddos"
    OUTPUTS: Path = DATA / "outputs"
    LOGS: Path = DATA / "logs"

if __name__ == "__main__":
    print(_ServiceType().METADATA)