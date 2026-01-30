# mypy: disable-error-code=call-overload
from logging import Logger, getLogger
from pathlib import Path

import orjson
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class JobSettings(BaseSettings):  # type: ignore[explicit-any]
    base_dir: Path = Field(alias="BASE_DIR")
    dids: list[str] = Field(alias="DIDS")
    transformation_did: str = Field(alias="TRANSFORMATION_DID")
    secret: str | None = Field(default=None, alias="SECRET")
    logger: Logger = Field(default_factory=lambda: getLogger(__name__))

    model_config = SettingsConfigDict(
        extra="forbid",
        validate_default=True,
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
