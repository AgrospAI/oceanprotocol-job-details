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

    dids: list[str | None]
    """Input DIDs, index-aligned with the ``/data/inputs/<index>`` folders"""

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

    def resolve_input(self, index: int, did: str | None) -> tuple[str, Path | None]:
        """Resolve the input folder of a job entry.

        Ocean Node >= 4.6 isolates every input in its own ``/data/inputs/<index>``
        folder and sends ``DIDS`` index-aligned with those folders, so the input is
        looked up by position first. Older nodes used ``/data/inputs/<did>``, which
        is kept as a fallback so the same algorithm works against both layouts.
        """
        identifier = did or str(index)
        indexed = self.paths.inputs / str(index)
        if indexed.is_dir() or indexed.is_file():
            return identifier, indexed
        if did is not None:
            legacy = self.calculate_path(did, "input")
            if legacy.is_dir() or legacy.is_file():
                return identifier, legacy
        return identifier, None

    @override
    def load(self) -> Files:
        res = []
        for index, did in enumerate(self.dids):
            identifier, input_path = self.resolve_input(index, did)

            ddo_path = self.calculate_path(identifier, "ddo")
            ddo = ddo_path if ddo_path.is_file() else None

            if input_path is None:
                input_files = []
            elif input_path.is_dir():
                input_files = [f for f in input_path.glob("*") if f.is_file()]
            elif input_path.is_file():
                input_files = [input_path]
            else:
                input_files = []

            res.append(
                DIDPaths(
                    did=identifier,
                    ddo=ddo,
                    input_files=input_files,
                )
            )
        return res
