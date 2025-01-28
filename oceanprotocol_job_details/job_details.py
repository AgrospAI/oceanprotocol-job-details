from typing import Literal, Optional

from oceanprotocol_job_details.dataclasses.job_details import JobDetails
from oceanprotocol_job_details.loaders.impl.environment import EnvironmentLoader
from oceanprotocol_job_details.loaders.loader import Loader

_Implementations = Literal["env"]


class OceanProtocolJobDetails(Loader[JobDetails]):
    """Decorator that loads the JobDetails from the given implementation"""

    def __init__(
        self,
        implementation: Optional[_Implementations] = "env",
        *args,
        **kwargs,
    ):
        if implementation == "env":
            # As there are not more implementations, we can use the EnvironmentLoader directly
            self._loader = lambda: EnvironmentLoader(*args, **kwargs)
        else:
            raise NotImplementedError(f"Implementation {implementation} not supported")

    def load(self) -> JobDetails:
        return self._loader().load()


del _Implementations
