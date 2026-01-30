from __future__ import annotations

from dataclasses import InitVar, dataclass, field
from logging import Logger
from pathlib import Path
from typing import Literal, final

from oceanprotocol_job_details.domain import DIDPaths, Files, Paths


@final
@dataclass(frozen=True)
class FilesLoader:
    paths: Paths
    """Path configurations of the project"""

    logger: Logger = field(repr=False)
    """Logger to use"""

    dids: list[str]
    """Input DIDs"""

    transformation_did: InitVar[str | None] = None
    """DID for the transformation algorithm"""

    _transformation_did: str = field(init=False)

    def __post_init__(self, transformation_did: str | None) -> None:
        object.__setattr__(self, "_transformation_did", transformation_did)

        assert self.dids, "Missing input DIDs"

    def calculate_path(self, did: str, path_type: Literal["input", "ddo"]) -> Path:
        match path_type:
            case "ddo":
                return self.paths.ddos / did
            case "input":
                return self.paths.inputs / did

    def load(self) -> Files:
        return [
            DIDPaths(
                did=did,
                ddo=self.calculate_path(did, "ddo"),
                files=self.calculate_path(did, "input").iterdir(),
            )
            for did in self.dids
        ]
