from ctypes import ArgumentError
import logging
import os
from typing import Any, Literal, Mapping, Optional

from oceanprotocol_job_details.dataclasses.job_details import JobDetails
from oceanprotocol_job_details.loaders.impl.map import Keys, Map
from oceanprotocol_job_details.loaders.loader import Loader

# Logging setup for the module
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(threadName)s] [%(levelname)s]  %(message)s",
    handlers=[logging.StreamHandler()],
)

_Implementations = Literal["map"]


class OceanProtocolJobDetails(Loader[JobDetails]):
    """Decorator that loads the JobDetails from the given implementation"""

    def __init__(
        self,
        implementation: Optional[_Implementations] = "map",
        mapper: Mapping[str, Any] = os.environ,
        keys: Keys = Keys(),
        *args,
        **kwargs,
    ):
        match implementation.lower():
            case "map":
                self._loader = lambda: Map(mapper=mapper, keys=keys, *args, **kwargs)
            case _:
                raise ArgumentError(f"Implementation {implementation} not valid")

    def load(self) -> JobDetails:
        return self._loader().load()


del _Implementations


def _main():
    """Main function to test functionalities"""

    # Re-define logging configuration
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(threadName)s] [%(levelname)s]  %(message)s",
        handlers=[logging.StreamHandler()],
        force=True,
    )

    job_details = OceanProtocolJobDetails().load()
    logging.info(f"Loaded job details: {job_details}")


if __name__ == "__main__":
    _main()
