from dataclasses import InitVar, dataclass, field
from pathlib import Path
from typing import Iterator, Sequence, final

import json

from oceanprotocol_job_details.config import config


@dataclass(frozen=True)
class DIDPaths:
    did: str
    ddo: Path
    input_files: Sequence[Path]

    def __post_init__(self) -> None:
        assert self.ddo.exists(), f"DDO {self.ddo} does not exist"
        for input_file in self.input_files:
            assert input_file.exists(), f"File {input_file} does not exist"

    def __len__(self) -> int:
        return len(self.input_files)


@dataclass(frozen=True)
class Files:
    files: Sequence[DIDPaths]

    def __iter__(self) -> Iterator[DIDPaths]:
        return iter(self.files)

    def __len__(self) -> int:
        return len(self.files)


@final
@dataclass(frozen=True)
class FilesLoader:
    dids: InitVar[str | None]
    """Input DIDs"""

    transformation_did: InitVar[str | None]
    """DID for the transformation algorithm"""

    _dids: Sequence[str] = field(init=False)
    _transformation_did: str = field(init=False)

    def __post_init__(
        self,
        dids: str | None,
        transformation_did: str | None,
    ) -> None:
        assert dids, "Missing DIDs"
        assert transformation_did, "Missing transformation DID"

        object.__setattr__(self, "_dids", json.loads(dids))
        object.__setattr__(self, "_transformation_did", transformation_did)

    def load(self) -> Files:
        files: list[DIDPaths] = []
        for did in self._dids:
            base = Path(config.path_inputs) / did
            files.append(
                DIDPaths(
                    did=did,
                    ddo=Path(config.path_ddos) / did,
                    input_files=list(base.iterdir()),
                )
            )

        return Files(files)
