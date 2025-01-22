import os
from dataclasses import dataclass
from json import load, loads
from pathlib import Path
from typing import Mapping, Optional, Sequence

from constants import DidKeys, EnvironmentKeys, Paths, ServiceType


@dataclass(frozen=True, slots=True)
class Algorithm:
    DID: str
    """The DID of the algorithm used to process the data"""

    DDO: Path
    """The DDO of the algorithm used to process the data"""

    @classmethod
    def from_environment(
        cls,
        env: os._Environ = os.environ,
        root: Path = None,
    ) -> "Algorithm" | None:
        """Load the used algorithm info"""

        did = env.get(EnvironmentKeys.ALGORITHM)

        if not did:
            return None

        if not root:
            root = env.get(EnvironmentKeys.ROOT)

        return cls(
            DID=did,
            DDO=root / Paths.DDOS / did,
        )


@dataclass(frozen=True, slots=True)
class JobDetails:
    """Constant paths to the different folders used by OceanProtocol"""

    _env: os._Environ[str]
    """Used environment variable"""

    ROOT: Path
    """The root folder of the Ocean Protocol directories"""

    DIDS: Optional[Sequence[Path]]
    """Identifiers for the inputs"""

    METADATA: Mapping
    # TODO: To define

    FILES: Mapping[str, Sequence[Path]]
    """Paths to the input files"""

    ALGORITHM: Optional[Algorithm]
    """Details of the used algorithm"""

    @classmethod
    def from_environment(
        cls,
        env: os._Environ = os.environ,
    ) -> "Paths":
        """Load all the paths from the current job environment"""

        # The root path for the rest of directories
        root = Path(env.get(EnvironmentKeys.ROOT, ""))

        dids = (
            loads(env.get(EnvironmentKeys.DIDS)) if EnvironmentKeys.DIDS in env else []
        )

        files: Mapping[str, Sequence[Path]] = {}
        for did in dids:
            # Retrieve DDO from disk
            file = root / Paths.DIDS / did
            with open(file, "r") as f:
                ddo = load(file)
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

        return cls(
            _env=env,
            ROOT=root,
            DIDS=dids,
            METADATA={},  # TODO
            FILES=files,
            ALGORITHM=Algorithm.from_environment(root, env),
        )

    @property
    def SECRET(self) -> Optional[str]:
        return self._env.get(EnvironmentKeys.SECRET, None)


# EXAMPLE
#
# def get_job_details():
#     job["dids"] = json.loads(os.getenv("DIDS", None))
#     job["metadata"] = dict()
#     job["files"] = dict()
#     job["algo"] = dict()
#     job["secret"] = os.getenv("secret", None)
#     algo_did = os.getenv("TRANSFORMATION_DID", None)
#     if job["dids"] is not None:
#         for did in job["dids"]:
#             # get the ddo from disk
#             filename = root + "/data/ddos/" + did
#             print(f"Reading json from {filename}")
#             with open(filename) as json_file:
#                 ddo = json.load(json_file)
#                 # search for metadata service
#                 for service in ddo["service"]:
#                     if service["type"] == "metadata":
#                         job["files"][did] = list()
#                         index = 0
#                         for file in service["attributes"]["main"]["files"]:
#                             job["files"][did].append(
#                                 root + "/data/inputs/" + did + "/" + str(index))
#                             index = index + 1
#     if algo_did is not None:
#         job["algo"]["did"] = algo_did
#         job["algo"]["ddo_path"] = root + "/data/ddos/" + algo_did
#     return job
