from dataclasses import InitVar, dataclass, field
from pathlib import Path
from typing import Sequence, final

from oceanprotocol_job_details.ocean import DDO
from oceanprotocol_job_details.utils import load_dataclass


@final
@dataclass(frozen=True)
class DDOLoader:

    ddo_paths: InitVar[Sequence[Path]]
    """The files to load the DDOs from"""

    _ddo_paths: Sequence[Path] = field(init=False)

    def __post_init__(self, ddo_paths: Sequence[Path]) -> None:
        assert ddo_paths, "Missing DDO paths"

        object.__setattr__(self, "_ddo_paths", ddo_paths)

    def load(self) -> Sequence[DDO]:
        ddos = []
        for path in self._ddo_paths:
            with open(path, "r") as f:
                ddos.append(load_dataclass(f.read(), DDO))
        return ddos
