from typing import Dict, Type, TypeAlias, TypeVar

from pydantic import BaseModel, JsonValue
from returns.io import IOFailure, IOSuccess
from returns.result import Failure, Success

from oceanprotocol_job_details.di import Container
from oceanprotocol_job_details.ocean import (
    EmptyJobDetails,
    JobDetails,
    ParametrizedJobDetails,
)
from oceanprotocol_job_details.settings import JobSettings

InputParametersT = TypeVar("InputParametersT", bound=BaseModel | None)
EmptyInputParameters: TypeAlias = BaseModel


def create_container(
    config: Dict[str, JsonValue],
) -> Container[InputParametersT]:
    """
    Return a fully configured Container from a config dict.
    """

    container = Container[InputParametersT]()
    settings = JobSettings(**config)  # type: ignore[arg-type]
    container.config.from_pydantic(settings)
    return container


def load_job_details(
    input_type: Type[InputParametersT] | None = None,
    config: Dict[str, JsonValue] = {},
) -> JobDetails[InputParametersT]:
    """
    Load a ParametrizedJobDetails for a given input_type using the config.
    """

    container: Container[InputParametersT] = create_container(config)
    return container.job_details_loader(input_type=input_type).load()


def load_parametrized_job_details(  # type: ignore[return]
    input_type: Type[InputParametersT],
    config: Dict[str, JsonValue] = {},
) -> ParametrizedJobDetails[InputParametersT]:
    """
    Load a ParametrizedJobDetails for a given input_type using the config.
    """

    container: Container[InputParametersT] = create_container(config)
    job_details = container.job_details_loader(input_type=input_type).load()

    match job_details.read():
        case Success(parametrized_job_details):
            return parametrized_job_details  # type: ignore[no-any-return]
        case Failure(error):
            raise error


async def aload_parametrized_job_details(  # type: ignore[return]
    input_type: Type[InputParametersT],
    config: Dict[str, JsonValue] = {},
) -> ParametrizedJobDetails[InputParametersT]:
    """
    Load a ParametrizedJobDetails for a given input_type using the config.
    """

    container: Container[InputParametersT] = create_container(config)
    job_details = container.job_details_loader(input_type=input_type).load()

    match await job_details.aread():
        case IOSuccess(Success(parametrized_job_details)):
            return parametrized_job_details  # type: ignore[no-any-return]
        case IOFailure(Failure(error)):
            raise error


def load_empty_job_details(
    config: Dict[str, JsonValue] = {},
) -> EmptyJobDetails[EmptyInputParameters]:
    """
    Load a EmptyJobDetails using the config.
    """

    container: Container[EmptyInputParameters] = create_container(config)
    job_details = container.job_details_loader(input_type=None).load()

    return EmptyJobDetails.model_validate(job_details, from_attributes=True)
