from dataclasses import InitVar, dataclass, field
from pathlib import Path
from typing import List, Optional, Tuple, final

from typing_extensions import override

from oceanprotocol_job_details.domain import DDO, DID, DDOMetadata, Files, Metadata
from oceanprotocol_job_details.loaders.loader import Loader
from oceanprotocol_job_details.plugins import register


@register("ddo")
@final
@dataclass(frozen=True)
class DDOLoader(Loader[DDOMetadata]):
    files: InitVar[Files]
    """The files to load the DDOs from"""

    _files: List[Tuple[DID, Optional[Path]]] = field(init=False)

    def __post_init__(self, files: Files) -> None:
        assert files is not None and len(files) != 0, "Missing files"
        object.__setattr__(self, "_files", [(f.did, f.ddo) for f in files])

    @override
    def load(self) -> DDOMetadata:
        result: DDOMetadata = {}
        for did, path in self._files:
            if path is not None and path.is_file():
                try:
                    result[did] = DDO.model_validate_json(path.read_bytes())
                    continue
                except Exception:
                    pass

            result[did] = DDO(
                id=did,
                metadata=Metadata(
                    description=did,
                    name=did,
                    type="dataset",
                    author="Unknown",
                    license="Unknown",
                ),
            )
        return result
