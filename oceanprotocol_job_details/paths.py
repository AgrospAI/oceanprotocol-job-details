from dataclasses import InitVar, dataclass, field
from pathlib import Path


@dataclass
class Paths:
    """Configuration class for the Ocean Protocol Job Details"""

    base_dir: InitVar[Path | None]

    _base: Path = field(init=False)

    def __post_init__(self, base_dir: Path | None) -> None:
        self._base = base_dir or Path("/data")

    @property
    def data(self) -> Path:
        return self._base

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
