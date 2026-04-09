from __future__ import annotations

from pathlib import Path
from typing import Generator, Generic, Tuple, Type, TypeVar, final

import aiofiles
from pydantic import BaseModel, ConfigDict, Secret, ValidationError

from oceanprotocol_job_details.domain import DDOMetadata, Files, Paths
from oceanprotocol_job_details.exceptions import JobDetailsError

InputParametersT = TypeVar("InputParametersT", bound=BaseModel)


def read_input_parameters(
    paths: Paths,
    input_type: Type[InputParametersT],
) -> InputParametersT | JobDetailsError:
    """Read the input parameters from the paths and validate with the given type.

    Args:
        paths (Paths): Paths containing the algorithm custom parameters path.
        input_type (Type[InputParametersT]): Pydantic BaseModel to validate the input parameters data.

    Returns:
        Union[InputParametersT, JobDetailsError]: InputParametersT instance or JobDetailsError
    """

    if not paths.algorithm_custom_parameters.exists():
        return JobDetailsError("Algorithm custom input file missing")

    raw = paths.algorithm_custom_parameters.read_text().strip()

    if not raw:
        return JobDetailsError("Algorithm custom input parameters is empty")

    try:
        assert issubclass(input_type, BaseModel)
        return input_type.model_validate_json(raw)
    except ValidationError as error:
        exception = JobDetailsError("Validation failed for input parameters")
        exception.__cause__ = error
        return exception


async def aread_input_parameters(
    paths: Paths,
    input_type: Type[InputParametersT],
) -> InputParametersT | JobDetailsError:
    """Read the input parameters from the paths and validate with the given type.

    Args:
        paths (Paths): Paths containing the algorithm custom parameters path.
        input_type (Type[InputParametersT]): Pydantic BaseModel to validate the input parameters data.

    Returns:
        Union[InputParametersT, JobDetailsError]: InputParametersT instance or JobDetailsError
    """

    if not paths.algorithm_custom_parameters.exists():
        return JobDetailsError("Algorithm custom input file missing")

    async with aiofiles.open(paths.algorithm_custom_parameters, "r") as f:
        raw = (await f.read()).strip()

    if not raw:
        return JobDetailsError("Algorithm custom input parameters is empty")

    try:
        assert issubclass(input_type, BaseModel)
        return input_type.model_validate_json(raw)
    except ValidationError as error:
        exception = JobDetailsError("Validation failed for input parameters")
        exception.__cause__ = error
        return exception


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

    async def aread(
        self,
    ) -> ParametrizedJobDetails[InputParametersT] | JobDetailsError:
        """Read the input parameters and get a ParametrizedJobDetails instance.

        Returns:
            Union[ParametrizedJobDetails[InputParametersT], JobDetailsError]: Success if the input_type is set.
        """

        if self.input_type is None:
            return JobDetailsError("JobDetails has no input parameters")

        result = await aread_input_parameters(self.paths, self.input_type)

        if isinstance(result, JobDetailsError):
            return result

        return ParametrizedJobDetails(
            input_parameters=result,
            **self.model_dump(exclude={"input_type"}),
        )

    def read(  # type: ignore[return]
        self,
    ) -> ParametrizedJobDetails[InputParametersT] | JobDetailsError:
        """Read the input parameters and get a ParametrizedJobDetails instance.

        Returns:
            Union[ParametrizedJobDetails[InputParametersT], JobDetailsError]: Success if the input_type is set.
        """

        if self.input_type is None:
            return JobDetailsError("JobDetails has no input parameters")

        result = read_input_parameters(self.paths, self.input_type)

        if isinstance(result, JobDetailsError):
            return result

        return ParametrizedJobDetails(
            input_parameters=result,
            **self.model_dump(exclude={"input_type"}),
        )


@final
class ParametrizedJobDetails(_BaseJobDetails[InputParametersT]):  # type: ignore[explicit-any]
    """Parametrized job details class with the loaded input parameters."""

    input_parameters: InputParametersT


@final
class EmptyJobDetails(_BaseJobDetails[InputParametersT]):  # type: ignore[explicit-any]
    """Empty job details class with no input parameters"""

    input_type: None = None
