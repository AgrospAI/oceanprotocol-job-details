from dataclasses import InitVar, dataclass, field
from pathlib import Path
from typing import Dict, Generator, List, Sequence, TypeAlias

from oceanprotocol_job_details.domain.ddo import DDO

DID: TypeAlias = str


@dataclass(frozen=True)
class DIDPaths:
    did: DID
    ddo: Path = field(repr=False)

    files: InitVar[Generator[Path, None, None]]

    _input: List[Path] = field(init=False, repr=False)

    def __post_init__(self, files: Generator[Path, None, None]) -> None:
        assert self.ddo.exists(), f"DDO {self.ddo} does not exist"

        object.__setattr__(self, "_input", list(files))

    @property
    def input_files(self) -> List[Path]:
        return self._input

    def __len__(self) -> int:
        return len(self._input)


Files: TypeAlias = Sequence[DIDPaths]


@dataclass(frozen=True)
class Paths:
    """Configuration class for the Ocean Protocol Job Details"""

    base_dir: Path = field(default_factory=lambda: Path("/data"))

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
