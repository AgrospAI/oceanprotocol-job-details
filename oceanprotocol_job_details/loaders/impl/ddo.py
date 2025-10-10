from __future__ import annotations

from dataclasses import InitVar, dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, final

if TYPE_CHECKING:
    from oceanprotocol_job_details.ocean import DDO, Files


@final
@dataclass(frozen=True)
class DDOLoader:

    files: InitVar[list[Files]]
    """The files to load the DDOs from"""

    _ddo_paths: list[Path] = field(init=False)

    def __post_init__(self, files: list[Files]) -> None:
        assert files, "Missing files"

        object.__setattr__(self, "_ddo_paths", [f.ddo for f in files])

    def load(self) -> list[DDO]:
        from oceanprotocol_job_details.ocean import DDO

        ddos = []
        for path in self._ddo_paths:
            with open(path, "r") as f:
                ddos.append(DDO.from_json(f.read()))
        return ddos
