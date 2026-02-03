# mypy: disable-error-code=call-overload
import sys
from logging import Logger, getLogger
from pathlib import Path

if sys.version_info >= (3, 11):
    from typing import Self
else:  # pragma: no cover
    from typing_extensions import Self

import orjson
from pydantic import Field, Secret, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class JobSettings(BaseSettings):  # type: ignore[explicit-any]
    base_dir: Path = Field(alias="BASE_DIR")
    dids: list[str] = Field(default_factory=list, alias="DIDS")
    transformation_did: str = Field(alias="TRANSFORMATION_DID")
    secret: Secret[str] | None = Field(default=None, alias="SECRET")
    logger: Logger = Field(default_factory=lambda: getLogger(__name__))

    model_config = SettingsConfigDict(
        extra="forbid",
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )

    @field_validator("dids", mode="before")
    @classmethod
    def split_dids(cls, v: list[str] | str) -> list[str]:
        if isinstance(v, str):
            data = orjson.loads(v)
            assert isinstance(data, list)
            return data
        return v

    @model_validator(mode="after")
    def validate_dids(self) -> Self:
        if len(self.dids) == 0:
            self.dids.extend(
                [f.name for f in (self.base_dir / "ddos").glob("*") if f.is_file()]
            )
        return self
