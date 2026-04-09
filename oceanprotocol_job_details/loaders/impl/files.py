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
        return [
            DIDPaths(
                did=did,
                ddo=self.calculate_path(did, "ddo"),
                input_files=list(self.calculate_path(did, "input").glob("*")),
            )
            for did in self.dids
        ]
