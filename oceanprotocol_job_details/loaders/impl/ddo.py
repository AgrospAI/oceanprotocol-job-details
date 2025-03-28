from dataclasses import InitVar, dataclass, field
from pathlib import Path
from typing import final

import orjson

from oceanprotocol_job_details.ocean import DDO
from oceanprotocol_job_details.utils import pydantic_to_dataclass


@final
@dataclass(frozen=True)
class DDOLoader:
    ddo_paths: InitVar[list[Path]]
    """The files to load the DDOs from"""

    _ddo_paths: list[Path] = field(init=False)

    def __post_init__(self, ddo_paths: list[Path]) -> None:
        assert ddo_paths, "Missing DDO paths"

        object.__setattr__(self, "_ddo_paths", ddo_paths)

    def load(self) -> list[DDO]:
        ddos = []
        for path in self._ddo_paths:
            with open(path, "r") as f:
                data = orjson.loads(f.read())
                ddos.append(pydantic_to_dataclass(DDO, data))
        return ddos
