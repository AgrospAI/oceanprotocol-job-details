from pathlib import Path
from typing import Dict, List, Sequence, TypeAlias

from pydantic import ConfigDict, Field
from pydantic.dataclasses import dataclass

from oceanprotocol_job_details.domain.ddo import DDO

DID: TypeAlias = str


@dataclass(config=ConfigDict(frozen=True, arbitrary_types_allowed=True, extra="forbid"))
class DIDPaths:
    did: DID
    ddo: Path

    input_files: List[Path] = Field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.ddo.exists():
            raise FileNotFoundError(f"DDO {self.ddo} does not exist")

    def __len__(self) -> int:
        return len(self.input_files)


Files: TypeAlias = Sequence[DIDPaths]


@dataclass(config=ConfigDict(frozen=True, arbitrary_types_allowed=True, extra="forbid"))
class Paths:
    """Configuration class for the Ocean Protocol Job Details"""

    base_dir: Path = Field(default_factory=lambda: Path("/data"))

    @property
    def data(self) -> Path:
        return self.base_dir

    @property
    def inputs(self) -> Path:
        return self.data / "inputs"

    @property
    def ddos(self) -> Path:
        return self.data / "ddos"

    @property
    def outputs(self) -> Path:
        return self.data / "outputs"

    @property
    def logs(self) -> Path:
        return self.data / "logs"

    @property
    def algorithm_custom_parameters(self) -> Path:
        return self.inputs / "algoCustomData.json"


DDOMetadata: TypeAlias = Dict[DID, DDO]
