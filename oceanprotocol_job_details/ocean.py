from __future__ import annotations

import asyncio
from functools import cached_property
from pathlib import Path
from typing import Generator, Generic, Tuple, Type, TypeVar, final

import aiofiles
from pydantic import BaseModel, ConfigDict, Secret, model_validator

from oceanprotocol_job_details.domain import DDO, Files, Paths

InputParemetersT = TypeVar("InputParemetersT", bound=BaseModel)


@final
class JobDetails(BaseModel, Generic[InputParemetersT]):  # type: ignore[explicit-any]
    files: Files
    ddos: list[DDO]
    paths: Paths
    input_type: Type[InputParemetersT]
    secret: Secret[str] | None = None

    model_config = ConfigDict(arbitrary_types_allowed=True, frozen=True)

    @model_validator(mode="after")
    def validate_type(self) -> JobDetails[InputParemetersT]:
        assert issubclass(self.input_type, BaseModel), (
            f"{self.input_type} must be subtype of pydantic.BaseModel"
        )
        return self

    def inputs(self) -> Generator[Tuple[int, Path], None, None]:
        yield from (
            (idx, file)
            for idx, files in enumerate(self.files)
            for file in files.input_files
        )

    @cached_property
    def input_parameters(self) -> InputParemetersT:
        return asyncio.run(self.ainput_parameters())

    async def ainput_parameters(self) -> InputParemetersT:
        path = self.paths.algorithm_custom_parameters
        async with aiofiles.open(path) as f:
            raw = await f.read()

        raw = raw.strip()
        assert raw is not None, f"Empty file {path}"
        return self.input_type.model_validate_json(raw)
