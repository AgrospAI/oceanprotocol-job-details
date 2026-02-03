from dataclasses import dataclass
from typing import Generic, Type, TypeVar, final

from pydantic import BaseModel, Secret

from oceanprotocol_job_details.domain import DDOMetadata, Files, Paths
from oceanprotocol_job_details.ocean import JobDetails

InputParameterT = TypeVar("InputParameterT", bound=BaseModel)


@final
@dataclass(frozen=True)
class JobDetailsLoader(Generic[InputParameterT]):
    input_type: Type[InputParameterT] | None
    files: Files
    secret: Secret[str] | None
    paths: Paths
    metadata: DDOMetadata

    def load(self) -> JobDetails[InputParameterT]:
        return JobDetails[InputParameterT](
            files=self.files,
            secret=self.secret,
            metadata=self.metadata,
            paths=self.paths,
            input_type=self.input_type,
        )
