from pathlib import Path
from typing import Generator, Generic, Tuple, Type, TypeVar, final

import aiofiles
import orjson
from pydantic import BaseModel, ConfigDict, Secret

from oceanprotocol_job_details.domain import DDOMetadata, Files, Paths

InputParametersT = TypeVar("InputParametersT", bound=BaseModel)


@final
class JobDetails(BaseModel, Generic[InputParametersT]):  # type: ignore[explicit-any]
    files: Files
    metadata: DDOMetadata
    paths: Paths
    input_type: Type[InputParametersT] | None = None
    secret: Secret[str] | None = None

    model_config = ConfigDict(arbitrary_types_allowed=True, frozen=True)

    _input_parameters: InputParametersT | None = None

    def inputs(self) -> Generator[Tuple[int, Path], None, None]:
        yield from (
            (idx, file)
            for idx, files in enumerate(self.files)
            for file in files.input_files
        )

    async def input_parameters(self) -> InputParametersT | None:
        current = self._input_parameters

        if current is None:
            current = await self.ainput_parameters()
            object.__setattr__(self, "_input_parameters", current)

        return current

    async def ainput_parameters(self) -> InputParametersT | None:
        if self.input_type is None:
            return None

        path = self.paths.algorithm_custom_parameters
        async with aiofiles.open(path) as f:
            raw = await f.read()

        raw = raw.strip()
        assert raw is not None, f"Empty file {path}"
        return self.input_type.model_validate(orjson.loads(raw))
