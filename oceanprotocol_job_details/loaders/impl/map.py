"""Loads the current Job Details from the environment variables, could be abstracted to a more general 'mapper loader' but won't, since right now it fits our needs"""

from dataclasses import dataclass
from json import JSONDecodeError, load, loads
from logging import getLogger
from pathlib import Path
from typing import Mapping, Optional, Sequence, final

from oceanprotocol_job_details.dataclasses.constants import DidKeys, Paths, ServiceType
from oceanprotocol_job_details.dataclasses.job_details import Algorithm, JobDetails
from oceanprotocol_job_details.loaders.impl.utils import do
from oceanprotocol_job_details.loaders.loader import Loader

logger = getLogger(__name__)


@dataclass(frozen=True)
class Keys:
    """Environment keys passed to the algorithm"""

    ROOT_FOLDER = "ROOT_FOLDER"
    SECRET: str = "secret"
    ALGORITHM: str = "TRANSFORMATION_DID"
    DIDS: str = "DIDS"


@final
class Map(Loader[JobDetails]):
    """Loads the current Job Details from the environment variables"""

    def __init__(self, mapper: Mapping[str, str], keys: Keys, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self._mapper = mapper
        self._keys = keys

        # Update the default Paths if the user has passed a root folder
        if Keys.ROOT_FOLDER in self._mapper:
            root = self._mapper[Keys.ROOT_FOLDER]

            # Update the rest of paths
            Paths.DATA = Path(root) / "data"
            Paths.INPUTS = Paths.DATA / "inputs"
            Paths.DDOS = Paths.DATA / "ddos"
            Paths.OUTPUTS = Paths.DATA / "outputs"
            Paths.LOGS = Paths.DATA / "logs"
            Paths.ALGORITHM_CUSTOM_PARAMETERS = Paths.INPUTS / "algoCustomData.json"

    def load(self, *args, **kwargs) -> JobDetails:
        dids = self._dids()

        return JobDetails(
            dids=dids,
            files=self._files(dids),
            algorithm=self._algorithm(),
            secret=self._secret(),
        )

    def _dids(self) -> Sequence[Path]:
        return (
            loads(self._mapper.get(self._keys.DIDS))
            if self._keys.DIDS in self._mapper
            else []
        )

    def _files(self, dids: Optional[Sequence[Path]]) -> Mapping[str, Sequence[Path]]:
        """Iterate through the given DIDs and retrieve their respective filepaths

        :param dids: dids to read the files from
        :type dids: Optional[Sequence[Path]]
        :raises FileNotFoundError: if the DDO file does not exist
        :return: _description_
        :rtype: Mapping[str, Sequence[Path]]
        """

        files: Mapping[str, Sequence[Path]] = {}

        for did in dids:
            # For each given DID, check if the DDO file exists and read its metadata

            file_path = Paths.DDOS / did
            if not file_path.exists():
                raise FileNotFoundError(f"DDO file {file_path} does not exist")

            with open(file_path, "r") as f:
                ddo = do(lambda: load(f), JSONDecodeError)
                if not ddo:
                    continue

                for service in do(lambda: ddo[DidKeys.SERVICE], KeyError, default=[]):
                    if service[DidKeys.SERVICE_TYPE] != ServiceType.METADATA:
                        continue  # Only read the metadata of the services

                    did_path = Paths.INPUTS / did
                    files[did] = [
                        did_path / str(idx)
                        for idx in range(
                            len(
                                service[DidKeys.ATTRIBUTES][DidKeys.MAIN][DidKeys.FILES]
                            )
                        )
                    ]

        return files

    def _algorithm(self) -> Optional[Algorithm]:
        did = self._mapper.get(self._keys.ALGORITHM, None)

        if not did:
            return None

        ddo = Paths.DDOS / did
        if not ddo.exists():
            raise FileNotFoundError(f"DDO file {ddo} does not exist")

        return Algorithm(did, ddo)

    def _secret(self) -> Optional[str]:
        return self._mapper.get(self._keys.SECRET, None)
