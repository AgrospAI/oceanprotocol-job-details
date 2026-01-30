from typing import Any, Dict, Type, TypeVar

from pydantic import BaseModel, JsonValue

from oceanprotocol_job_details.di import Container
from oceanprotocol_job_details.ocean import JobDetails
from oceanprotocol_job_details.settings import JobSettings

InputParametersT = TypeVar("InputParametersT", bound=BaseModel)


def create_container(config: Dict[str, Any]) -> Container[InputParametersT]:  # type: ignore[explicit-any]
    """Return a fully configured Container from a config dict."""
    container = Container[InputParametersT]()
    settings = JobSettings(**config)
    container.config.from_pydantic(settings)
    return container


def load_job_details(
    config: Dict[str, JsonValue],
    input_type: Type[InputParametersT],
) -> JobDetails[InputParametersT]:
    """
    Load JobDetails for a given input_type using the config.
    Returns a fully initialized JobDetails instance.
    """
    container: Container[InputParametersT] = create_container(config)
    return container.job_details_loader(input_type=input_type).load()
