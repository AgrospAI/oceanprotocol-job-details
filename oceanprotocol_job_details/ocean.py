from __future__ import annotations

import asyncio
from functools import cached_property
from pathlib import Path
from typing import Generator, Generic, Tuple, Type, TypeVar, final

import aiofiles
from pydantic import BaseModel, ConfigDict, Secret

from oceanprotocol_job_details.domain import DDO, Files, Paths
from oceanprotocol_job_details.executors import run_in_executor

InputParametersT = TypeVar("InputParametersT", BaseModel, None)


@final
class JobDetails(BaseModel, Generic[InputParametersT]):  # type: ignore[explicit-any]
    files: Files
    ddos: list[DDO]
    paths: Paths
    input_type: Type[InputParametersT] | None
    secret: Secret[str] | None = None

    model_config = ConfigDict(arbitrary_types_allowed=True, frozen=True)

    _input_parameters: InputParametersT | None = None

    def inputs(self) -> Generator[Tuple[int, Path], None, None]:
        yield from (
            (idx, file)
            for idx, files in enumerate(self.files)
            for file in files.input_files
        )

    async def input_parameters(self) -> InputParametersT:
        if self._input_parameters is None:
            input_parameters = await self.ainput_parameters()
            object.__setattr__(self, "_input_parameters", input_parameters)
        return self._input_parameters

    async def ainput_parameters(self) -> InputParametersT:
        if self.input_type is None:
            return None

        path = self.paths.algorithm_custom_parameters
        async with aiofiles.open(path) as f:
            raw = await f.read()

        raw = raw.strip()
        assert raw is not None, f"Empty file {path}"
        return self.input_type.model_validate_json(raw)  # type: ignore
