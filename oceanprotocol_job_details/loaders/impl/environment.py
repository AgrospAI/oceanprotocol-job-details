"""Loads the current Job Details from the environment variables, could be abstracted to a more general 'mapper loader' but won't, since right now it fits our needs"""

import os
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from json import JSONDecodeError, load, loads
from logging import getLogger
from pathlib import Path
from typing import Optional, final

from oceanprotocol_job_details.dataclasses.constants import DidKeys, Paths, ServiceType
from oceanprotocol_job_details.dataclasses.job_details import Algorithm, JobDetails
from oceanprotocol_job_details.loaders.loader import Loader

logger = getLogger(__name__)


@dataclass(frozen=True)
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

    def load(self, *args, **kwargs) -> JobDetails:
        root, dids = self._root(), self._dids()

        return JobDetails(
            root=root,
            dids=dids,
            files=self._files(root, dids),
            algorithm=self._algorithm(root),
            secret=self._secret(),
        )

    def _root(self) -> Path:
        root = Path(self.mapper.get(Keys.ROOT, Path.home()))

        if not root.exists():
            raise FileNotFoundError(f"Root folder {root} does not exist")

        return root

    def _dids(self) -> Sequence[Path]:
        return loads(self.mapper.get(Keys.DIDS)) if Keys.DIDS in self.mapper else []

    def _files(
        self,
        root: Path,
        dids: Optional[Sequence[Path]],
    ) -> Mapping[str, Sequence[Path]]:

        files: Mapping[str, Sequence[Path]] = {}

        for did in dids:
            # Retrieve DDO from disk
            file_path = root / Paths.DDOS / did
            if not file_path.exists():
                raise FileNotFoundError(f"DDO file {file_path} does not exist")

            with open(file_path, "r") as f:
                try:
                    ddo = load(f)
                except JSONDecodeError as e:
                    logger.warning(f"Error loading DDO file {file_path}: {e}")
                    continue

                for service in ddo[DidKeys.SERVICE]:
                    if service[DidKeys.SERVICE_TYPE] != ServiceType.METADATA:
                        continue

                    did_path = root / Paths.INPUTS / did
                    files[did] = [
                        did_path / str(idx)
                        for idx in range(
                            len(
                                service[DidKeys.ATTRIBUTES][DidKeys.MAIN][DidKeys.FILES]
                            )
                        )
                    ]

        return files

    def _algorithm(self, root: Path) -> Optional[Algorithm]:
        did = self.mapper.get(Keys.ALGORITHM, None)

        if not did:
            return None

        ddo = root / Paths.DDOS / did
        if not ddo.exists():
            raise FileNotFoundError(f"DDO file {ddo} does not exist")

        return Algorithm(did, ddo)

    def _secret(self) -> Optional[str]:
        return self.mapper.get(Keys.SECRET, None)
