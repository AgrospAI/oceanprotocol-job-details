import logging
import os
from typing import Generic, TypeVar

from oceanprotocol_job_details.loaders.impl.job_details import JobDetailsLoader
from oceanprotocol_job_details.loaders.loader import Loader
from oceanprotocol_job_details.ocean import JobDetails

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(threadName)s] [%(levelname)s]  %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

T = TypeVar("T")


class OceanProtocolJobDetails(Generic[T]):
    """The JobDetails class is a dataclass that holds the details of the current job.

    Loading it will check the following:
    1. That the needed environment variables are set
    1. That the ocean protocol contains the needed data based on the passed environment variables

    Those needed environment variables are:
    - DIDS: The DIDs of the inputs
    - TRANSFORMATION_DID: The DID of the transformation algorithm
    - SECRET (optional): A really secret secret

    """

    def __init__(self) -> None:
        self.job_details_loader: Loader[JobDetails[T]] = JobDetailsLoader(
            os.environ.get("DIDS"),
            os.environ.get("TRANSFORMATION_DID"),
        )

    def load(self) -> JobDetails[T]:
        return self.job_details_loader().load()  # type:  ignore
