from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Generic, Type, TypeVar, final

from oceanprotocol_job_details.paths import Paths

if TYPE_CHECKING:
    from oceanprotocol_job_details.ocean import DDO, Files, JobDetails


T = TypeVar("T")


@final
@dataclass(frozen=True)
class JobDetailsLoader(Generic[T]):

    _type: Type[T] = field(repr=False)

    files: Files
    secret: str
    paths: Paths
    ddos: list[DDO]

    def load(self) -> JobDetails[T]:
        from oceanprotocol_job_details.ocean import JobDetails

        return JobDetails(
            files=self.files,
            secret=self.secret,
            ddos=self.ddos,
            paths=self.paths,
            _type=self._type,
        )
