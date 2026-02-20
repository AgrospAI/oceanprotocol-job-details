from __future__ import annotations

from pathlib import Path
from typing import Generator, Generic, Tuple, Type, TypeVar, final

import aiofiles
from pydantic import BaseModel, ConfigDict, Secret, ValidationError
from returns.io import IOFailure, IOResult, IOSuccess
from returns.result import Failure, Result, Success

from oceanprotocol_job_details.domain import DDOMetadata, Files, Paths
from oceanprotocol_job_details.exceptions import JobDetailsError

InputParametersT = TypeVar("InputParametersT", bound=BaseModel)


def read_input_parameters(
    paths: Paths,
    input_type: Type[InputParametersT],
) -> Result[InputParametersT, JobDetailsError]:
    """Read the input parameters from the paths and validate with the given type.

    Args:
        paths (Paths): Paths containing the algorithm custom parameters path.
        input_type (Type[InputParametersT]): Pydantic BaseModel to validate the input parameters data.

    Returns:
        Result[InputParametersT, JobDetailsError]: Result containing an InputParametersT instance or JobDetailsError
    """

    if not paths.algorithm_custom_parameters.exists():
        return Failure(JobDetailsError("Algorithm custom input file missing"))

    raw = paths.algorithm_custom_parameters.read_text().strip()

    if raw is None:
        return Failure(JobDetailsError("Algorithm custom input parameters is empty"))

    try:
        return Success(input_type.model_validate_json(raw))
    except ValidationError as error:
        return Failure(JobDetailsError(__cause__=error))


async def aread_input_parameters(
    paths: Paths,
    input_type: Type[InputParametersT],
) -> IOResult[InputParametersT, JobDetailsError]:
    """Read the input parameters from the paths and validate with the given type.

    Args:
        paths (Paths): Paths containing the algorithm custom parameters path.
        input_type (Type[InputParametersT]): Pydantic BaseModel to validate the input parameters data.

    Returns:
        Result[InputParametersT, JobDetailsError]: Result containing an InputParametersT instance or JobDetailsError
    """

    if not paths.algorithm_custom_parameters.exists():
        return IOFailure(JobDetailsError("Algorithm custom input file missing"))

    async with aiofiles.open(paths.algorithm_custom_parameters, "r") as f:
        raw = (await f.read()).strip()

    if raw is None:
        return IOFailure(JobDetailsError("Algorithm custom input parameters is empty"))

    try:
        return IOSuccess(input_type.model_validate_json(raw))
    except ValidationError as error:
        return IOFailure(JobDetailsError(__cause__=error))


class _BaseJobDetails(BaseModel, Generic[InputParametersT]):  # type: ignore[explicit-any]
    """Shared fields for all job types"""

    files: Files
    """The provider loaded DID and DDO files"""

    metadata: DDOMetadata
    """Dict with the DDO contents of each DID"""

    paths: Paths
    """Main used paths"""

    input_type: Type[InputParametersT] | None = None
    """Algorithm's custom input type"""

    secret: Secret[str] | None = None
    """Secret loaded from environment"""

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        frozen=True,
        from_attributes=True,
    )

    def inputs(self) -> Generator[Tuple[str, Path], None, None]:
        """
        Iterate through tuples containing the DID and the Path of each input file.
        The same DID may have multiple input files.
        """

        yield from (
            (file.parent.name, file)
            for files in self.files
            for file in files.input_files
        )


class JobDetails(_BaseJobDetails[InputParametersT]):  # type: ignore[explicit-any]
    """Class holding the OceanProtocol job details."""

    async def aread(  # type: ignore[return]
        self,
    ) -> IOResult[ParametrizedJobDetails[InputParametersT], JobDetailsError]:
        """Read the input parameters and get a ParametrizedJobDetails instance.

        Returns:
            IOResult[ParametrizedJobDetails[InputParametersT], JobDetailsError]: Success if the input_type is set.
        """

        if self.input_type is None:
            return IOFailure(JobDetailsError("JobDetails has no input parameters"))

        match await aread_input_parameters(self.paths, self.input_type):
            case IOSuccess(Success(input_parameters)):
                return IOSuccess(
                    ParametrizedJobDetails(
                        input_parameters=input_parameters,
                        **self.model_dump(exclude={"input_type"}),
                    )
                )
            case IOFailure(Failure(error)):
                return IOFailure(JobDetailsError(__cause__=error))

    def read(  # type: ignore[return]
        self,
    ) -> Result[ParametrizedJobDetails[InputParametersT], JobDetailsError]:
        """Read the input parameters and get a ParametrizedJobDetails instance.

        Returns:
            Result[ParametrizedJobDetails[InputParametersT], JobDetailsError]: Success if the input_type is set.
        """

        if self.input_type is None:
            return Failure(JobDetailsError("JobDetails has no input parameters"))

        match read_input_parameters(self.paths, self.input_type):
            case Success(input_parameters):
                return Success(
                    ParametrizedJobDetails(
                        input_parameters=input_parameters,
                        **self.model_dump(exclude={"input_type"}),
                    )
                )
            case Failure(error):
                return Failure(JobDetailsError(__cause__=error))


@final
class ParametrizedJobDetails(_BaseJobDetails[InputParametersT]):  # type: ignore[explicit-any]
    """Parametrized job details class with the loaded input parameters."""

    input_parameters: InputParametersT


@final
class EmptyJobDetails(_BaseJobDetails[InputParametersT]):  # type: ignore[explicit-any]
    """Empty job details class with no input parameters"""

    input_type: None = None
