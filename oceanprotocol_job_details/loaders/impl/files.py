from dataclasses import dataclass, field
from logging import Logger
from pathlib import Path
from typing import Literal, final

from typing_extensions import override

from oceanprotocol_job_details.domain import DIDPaths, Files, Paths
from oceanprotocol_job_details.loaders.loader import Loader
from oceanprotocol_job_details.plugins import register


@register("files")
@final
@dataclass(frozen=True)
class FilesLoader(Loader[Files]):
    paths: Paths
    """Path configurations of the project"""

    logger: Logger = field(repr=False)
    """Logger to use"""

    dids: list[str]
    """Input DIDs"""

    transformation_did: str
    """DID for the transformation algorithm"""

    def __post_init__(self) -> None:
        assert self.dids, "Missing input DIDs"

    def calculate_path(self, did: str, path_type: Literal["input", "ddo"]) -> Path:
        match path_type:
            case "ddo":
                return self.paths.ddos / did
            case "input":
                return self.paths.inputs / did

    @override
    def load(self) -> Files:
        res = []
        for did in self.dids:
            ddo_path = self.calculate_path(did, "ddo")
            ddo = ddo_path if ddo_path.is_file() else None

            input_path = self.calculate_path(did, "input")
            if input_path.is_dir():
                input_files = [f for f in input_path.glob("*") if f.is_file()]
            elif input_path.is_file():
                input_files = [input_path]
            else:
                input_files = []

            res.append(
                DIDPaths(
                    did=did,
                    ddo=ddo,
                    input_files=input_files,
                )
            )
        return res
