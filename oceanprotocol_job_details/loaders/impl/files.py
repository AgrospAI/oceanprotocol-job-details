from __future__ import annotations

import json
from dataclasses import InitVar, dataclass, field
from logging import Logger
from typing import TYPE_CHECKING, final

from oceanprotocol_job_details.paths import Paths

if TYPE_CHECKING:
    from oceanprotocol_job_details.ocean import DIDPaths, Files


@final
@dataclass(frozen=True)
class FilesLoader:

    dids: InitVar[str | None]
    """Input DIDs"""

    transformation_did: InitVar[str | None]
    """DID for the transformation algorithm"""

    paths: Paths
    """Path configurations of the project"""

    logger: Logger
    """Logger to use"""

    _dids: str = field(init=False)
    _transformation_did: str = field(init=False)

    def __post_init__(
        self,
        dids: str | None,
        transformation_did: str | None,
    ) -> None:
        def _load_dids(dids, logger):
            if dids:
                return json.loads(dids)

            logger.info("Missing DIDS, Inferring DIDS from input DDOs")
            return [f.parts[-1] for f in self.paths.ddos.iterdir()]

        object.__setattr__(self, "_transformation_did", transformation_did)
        object.__setattr__(self, "_dids", _load_dids(dids, self.logger))

        assert self._dids, "Missing input DIDs"

    def load(self) -> Files:
        from oceanprotocol_job_details.ocean import DIDPaths, Files

        files: list[DIDPaths] = []
        for did in self._dids:
            base = self.paths.inputs / did
            files.append(
                DIDPaths(
                    did=did,
                    ddo=self.paths.ddos / did,
                    input_files=list(base.iterdir()),
                )
            )

        return Files(files)
