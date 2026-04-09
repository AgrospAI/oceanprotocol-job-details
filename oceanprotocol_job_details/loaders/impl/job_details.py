from dataclasses import dataclass
from typing import Generic, Type, TypeVar, final

from pydantic import BaseModel, Secret
from typing_extensions import override

from oceanprotocol_job_details.domain import DDOMetadata, Files, Paths
from oceanprotocol_job_details.loaders.loader import Loader
from oceanprotocol_job_details.ocean import JobDetails
from oceanprotocol_job_details.plugins import register

InputParametersT = TypeVar("InputParametersT", bound=BaseModel | None)


@register("jobdetails")
@final
@dataclass(frozen=True)
class JobDetailsLoader(Loader[JobDetails[InputParametersT]], Generic[InputParametersT]):
    files: Files
    secret: Secret[str] | None
    paths: Paths
    metadata: DDOMetadata
    input_type: Type[InputParametersT] | None = None

    @override
    def load(self) -> JobDetails[InputParametersT]:
        return JobDetails[InputParametersT](
            files=self.files,
            secret=self.secret,
            metadata=self.metadata,
            paths=self.paths,
            input_type=self.input_type,
        )
