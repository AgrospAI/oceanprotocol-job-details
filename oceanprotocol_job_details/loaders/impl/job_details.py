import os
from dataclasses import dataclass, field
from typing import Generic, Type, TypeVar, final

from oceanprotocol_job_details.loaders.impl.ddo import DDOLoader
from oceanprotocol_job_details.loaders.impl.files import FilesLoader
from oceanprotocol_job_details.ocean import JobDetails

T = TypeVar("T")


@final
@dataclass(frozen=True)
class JobDetailsLoader(Generic[T]):
    _type: Type[T] = field(repr=False)
    

    def load(self) -> JobDetails[T]:
        dids = os.environ.get("DIDS")
        transformation_did = os.environ.get("TRANSFORMATION_DID")
        secret = os.environ.get("SECRET")

        files = FilesLoader(dids, transformation_did).load()
        ddos = DDOLoader([f.ddo for f in files]).load()

        return JobDetails(files=files, secret=secret, ddos=ddos, _type=self._type)
