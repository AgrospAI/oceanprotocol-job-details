from __future__ import annotations

from dataclasses import InitVar, dataclass, field
from pathlib import Path
from typing import final

from oceanprotocol_job_details.domain import DDO, Files


@final
@dataclass(frozen=True)
class DDOLoader:
    files: InitVar[Files]
    """The files to load the DDOs from"""

    _ddo_paths: list[Path] = field(init=False)

    def __post_init__(self, files: Files) -> None:
        assert files is not None and len(files) != 0, "Missing files"

        object.__setattr__(self, "_ddo_paths", [f.ddo for f in files])

    def load(self) -> list[DDO]:
        return [DDO.model_validate_json(p.read_text()) for p in self._ddo_paths]
