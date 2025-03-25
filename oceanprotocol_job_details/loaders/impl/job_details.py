import os
from dataclasses import dataclass
from typing import Generic, TypeVar, final

from oceanprotocol_job_details.loaders.impl.ddo import DDOLoader
from oceanprotocol_job_details.loaders.impl.files import FilesLoader
from oceanprotocol_job_details.ocean import JobDetails

T = TypeVar("T")


@final
@dataclass(frozen=True)
class JobDetailsLoader(Generic[T]):

    dids: str | None
    """Input DIDs"""

    transformation_did: str | None
    """DID for the transformation algorithm"""

    def __post_init__(self) -> None:
        assert "SECRET" in os.environ, "Missing SECRET environment variable"

    def load(self) -> JobDetails[T]:
        files = FilesLoader(self.dids, self.transformation_did).load()
        ddos = DDOLoader([f.ddo for f in files]).load()

        return JobDetails(
            files,
            os.environ.get("SECRET"),
        )
