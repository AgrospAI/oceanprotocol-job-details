"""Loads the current Job Details from the environment variables, could be abstracted to a more general 'mapper loader' but won't, since right now it fits our needs"""

import os
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from json import load, loads
from pathlib import Path
from typing import Optional, final, override

from src.oceanprotocol_job_details.dataclasses.constants import (
    DidKeys,
    Paths,
    ServiceType,
)
from src.oceanprotocol_job_details.dataclasses.job_details import Algorithm, JobDetails
from src.oceanprotocol_job_details.loaders.loader import Loader


@dataclass(frozen=True, slots=True)
class _Keys:
    """Environment keys passed to the algorithm"""

    ROOT: str = "ROOT_FOLDER"
    SECRET: str = "secret"
    ALGORITHM: str = "TRANSFORMATION_DID"
    DIDS: str = "DIDS"


Keys = _Keys()
del _Keys


@final
class EnvironmentLoader(Loader[JobDetails]):
    """Loads the current Job Details from the environment variables"""

    def __init__(self, mapper: Mapping[str, str] = os.environ):
        super().__init__()
        self.mapper = mapper

    @override
    def load(self, *args, **kwargs) -> JobDetails:
        root, dids = self._root(), self._dids()

        return JobDetails(
            root=root,
            dids=dids,
            metadata=self._metadata(),
            files=self._files(root, dids),
            algorithm=self._algorithm(root=root),
            secret=self._secret(),
        )

    def _root(self) -> Path:
        return Path(self.mapper.get(Keys.ROOT, ""))

    def _dids(self) -> Sequence[str]:
        return loads(self.mapper.get(Keys.DIDS)) if Keys.DIDS in self.mapper else []

    def _files(
        self,
        root: Path,
        dids: Optional[Sequence[Path]],
    ) -> Mapping[str, Sequence[Path]]:
        files: Mapping[str, Sequence[Path]] = {}
        for did in dids:
            # Retrieve DDO from disk
            file = root / Paths.DDOS / did
            with open(file, "r") as f:
                ddo = load(f)
                for service in ddo[DidKeys.SERVICE]:
                    if service[DidKeys.SERVICE_TYPE] == ServiceType.METADATA:
                        base_path = root / Paths.INPUTS / did
                        files[did] = [
                            base_path / str(idx)
                            for idx in range(
                                len(
                                    service[DidKeys.ATTRIBUTES][DidKeys.MAIN][
                                        DidKeys.FILES
                                    ]
                                )
                            )
                        ]
        return files

    def _metadata(self) -> Mapping[str, str]:
        return {}

    def _algorithm(self, root: Path) -> Algorithm:
        did = self.mapper.get(Keys.ALGORITHM, None)
        if not did:
            return None
        return Algorithm(
            did=did,
            ddo=root / Paths.DDOS / did,
        )

    def _secret(self) -> str:
        return self.mapper.get(Keys.SECRET, "")
