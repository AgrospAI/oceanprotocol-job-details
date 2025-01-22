import os
from dataclasses import dataclass
from json import load, loads
from pathlib import Path
from typing import Mapping, Optional, Sequence

from .constants import _DidKeys, _EnvironmentKeys, _Paths, _ServiceType

DidKeys = _DidKeys()
EnvironmentKeys = _EnvironmentKeys()
Paths = _Paths()
ServiceType = _ServiceType()


@dataclass(frozen=True, slots=True)
class Algorithm:
    DID: str
    """The DID of the algorithm used to process the data"""

    DDO: Path
    """The DDO path of the algorithm used to process the data"""

    @classmethod
    def from_environment(
        cls,
        env: os._Environ = os.environ,
        root: Path = None,
    ) -> Optional["Algorithm"]:
        """Load the used algorithm info from the given environment"""

        did = env.get(EnvironmentKeys.ALGORITHM, None)

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
    """TODO: To define"""

    FILES: Mapping[str, Sequence[Path]]
    """Paths to the input files"""

    ALGORITHM: Optional[Algorithm]
    """Details of the used algorithm"""

    @classmethod
    def from_environment(
        cls,
        env: os._Environ = os.environ,
    ) -> "JobDetails":
        """Load all the details from the current job environment"""

        root = Path(env.get(EnvironmentKeys.ROOT, ""))

        dids = (
            loads(env.get(EnvironmentKeys.DIDS)) if EnvironmentKeys.DIDS in env else []
        )

        # Refactor
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

        return cls(
            _env=env,
            ROOT=root,
            DIDS=dids,
            METADATA={},  # TODO
            FILES=files,
            ALGORITHM=Algorithm.from_environment(
                env=env,
                root=root,
            ),
        )

    @property
    def SECRET(self) -> Optional[str]:
        return self._env.get(EnvironmentKeys.SECRET, None)
