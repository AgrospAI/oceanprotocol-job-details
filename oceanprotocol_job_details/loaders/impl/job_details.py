from dataclasses import dataclass, field
from typing import Generic, Type, TypeVar, final

from pydantic import BaseModel

from oceanprotocol_job_details.domain import DDO, Files, Paths
from oceanprotocol_job_details.ocean import JobDetails

T = TypeVar("T", bound=BaseModel)


@final
@dataclass(frozen=True)
class JobDetailsLoader(Generic[T]):
    input_type: Type[T] = field(repr=False)
    files: Files
    secret: str
    paths: Paths
    ddos: list[DDO]

    def load(self) -> JobDetails[T]:
        return JobDetails[T](
            files=self.files,
            secret=self.secret,
            ddos=self.ddos,
            paths=self.paths,
            input_type=self.input_type,
        )
