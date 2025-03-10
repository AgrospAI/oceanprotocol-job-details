"""Loads the current Job Details from the environment variables, could be abstracted to a more general 'mapper loader' but won't, since right now it fits our needs"""

from dataclasses import dataclass
from logging import getLogger
from pathlib import Path
from typing import Mapping, Optional, Sequence, final

from orjson import JSONDecodeError, loads

from oceanprotocol_job_details.dataclasses.constants import DidKeys, Paths, ServiceType
from oceanprotocol_job_details.dataclasses.job_details import Algorithm, JobDetails
from oceanprotocol_job_details.loaders.impl.utils import do, execute_predicate
from oceanprotocol_job_details.loaders.loader import Loader

logger = getLogger(__name__)


@dataclass(frozen=True)
class Keys:
    """Environment keys passed to the algorithm"""

    ROOT_FOLDER = "ROOT_FOLDER"
    SECRET: str = "secret"
    ALGORITHM: str = "TRANSFORMATION_DID"
    DIDS: str = "DIDS"


def _update_paths_from_root(root: Path):
    """Update the default from a root folder

    :param root: root folder to update the paths
    :type root: Path
    """

    Paths.DATA = root / "data"
    Paths.INPUTS = Paths.DATA / "inputs"
    Paths.DDOS = Paths.DATA / "ddos"
    Paths.OUTPUTS = Paths.DATA / "outputs"
    Paths.LOGS = Paths.DATA / "logs"
    Paths.ALGORITHM_CUSTOM_PARAMETERS = Paths.INPUTS / "algoCustomData.json"


def _files_from_service(service):
    files = service[DidKeys.FILES]
    if isinstance(files, str):
        return [files]
    return files


@final
class Map(Loader[JobDetails]):
    """Loads the current Job Details from the environment variables"""

    def __init__(self, mapper: Mapping[str, str], keys: Keys, *args, **kwargs) -> None:
        self._mapper = mapper
        self._keys = keys

        execute_predicate(
            lambda: _update_paths_from_root(Path(self._mapper[Keys.ROOT_FOLDER])),
            lambda: Keys.ROOT_FOLDER in self._mapper,
        )

    def load(self, *args, **kwargs) -> JobDetails:
        return self._from_dids(self._dids())

    def _from_dids(self, dids: Sequence[str]) -> JobDetails:
        return JobDetails(
            dids=dids,
            files=self._files(dids),
            algorithm=self._algorithm(),
            secret=self._secret(),
        )

    def _dids(self) -> Sequence[str]:
        return loads(self._mapper.get(self._keys.DIDS, []))

    def _files(self, dids: Optional[Sequence[str]]) -> Mapping[str, Sequence[Path]]:
        """Iterate through the given DIDs and retrieve their respective filepaths

        :param dids: dids to read the files from
        :type dids: Optional[Sequence[str]]
        :raises FileNotFoundError: if the DDO file does not exist
        :return: _description_
        :rtype: Mapping[str, Sequence[Path]]
        """

        files: Mapping[str, Sequence[Path]] = {}
        for did in dids:
            # For each given DID, check if the DDO file exists and read its metadata
            ddo_path = Paths.DDOS / did
            do(lambda: ddo_path.exists(), exc=FileNotFoundError("Missing DDO file"))

            with open(ddo_path, "r") as f:
                ddo = do(lambda: loads(f.read()), JSONDecodeError)
                if not ddo:
                    continue

                for service in do(lambda: ddo[DidKeys.SERVICES], KeyError, default=[]):
                    # if service[DidKeys.SERVICE_TYPE] != ServiceType.METADATA:
                    #     continue  # Only read the metadata of the services

                    files_n = do(lambda: len(_files_from_service(service)), KeyError)
                    ddo_path = Paths.INPUTS / did
                    files[did] = [ddo_path / str(idx) for idx in range(files_n)]
        return files

    def _algorithm(self) -> Optional[Algorithm]:
        did = self._mapper.get(self._keys.ALGORITHM, None)
        if not did:
            return None

        ddo = Paths.DDOS / did

        return Algorithm(
            did,
            do(lambda: ddo.exists() and ddo, exc=FileNotFoundError("Missing DDO file")),
        )

    def _secret(self) -> Optional[str]:
        return self._mapper.get(self._keys.SECRET, None)
