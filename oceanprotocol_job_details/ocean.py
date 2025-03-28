from dataclasses import dataclass, field
from datetime import datetime
from functools import cached_property
from typing import Generic, Type, TypeVar, final

from pydantic import BaseModel, Field, HttpUrl

from oceanprotocol_job_details.config import config
from oceanprotocol_job_details.loaders.impl.files import Files
from oceanprotocol_job_details.utils import load_dataclass


T = TypeVar("T")


class Credential(BaseModel):  # type: ignore
    type: str
    values: list[str]


class Credentials(BaseModel):  # type: ignore
    allow: list[Credential]
    deny: list[Credential]


class Metadata(BaseModel):  # type: ignore
    description: str
    name: str
    type: str
    author: str
    license: str

    algorithm: str  # TODO: Add Algorithm class
    tags: list[str] | None = None
    created: datetime | None = None
    updated: datetime | None = None
    copyrightHolder: str | None = None
    links: list[HttpUrl] | None = None
    contentLanguage: str | None = None
    categories: list[str] | None = None


class ConsumerParameters(BaseModel):  # type: ignore
    name: str
    type: str
    label: str
    required: bool
    description: str
    default: str

    option: list[str] | None = None


class Service(BaseModel):  # type: ignore
    id: str
    type: str
    timeout: int
    files: str
    datatokenAddress: str
    serviceEndpoint: HttpUrl

    consumerParameters: ConsumerParameters
    additionalInformation: str
    name: str | None = None
    description: str | None = None


class Event(BaseModel):  # type: ignore
    tx: str
    block: int
    from_: str = Field(alias="from")
    contract: str
    datetime: datetime


class NFT(BaseModel):  # type: ignore
    address: str
    name: str
    symbol: str
    state: int
    tokenURI: HttpUrl
    owner: str
    created: datetime


class DataToken(BaseModel):  # type: ignore
    address: str
    name: str
    symbol: str
    serviceId: datetime


class Price(BaseModel):  # type: ignore
    value: int


class Stats(BaseModel):  # type: ignore
    allocated: int
    orders: int
    price: Price


class DDO(BaseModel):  # type: ignore
    id: str
    context: list[str] = Field(alias="@context")
    nftAddress: str
    chainId: int
    version: str
    metadata: Metadata
    services: list[Service]
    credentials: Credentials
    event: Event
    nft: NFT
    datatokens: list[DataToken]
    stats: Stats


@final
@dataclass(frozen=True)
class JobDetails(Generic[T]):
    files: Files
    """The input filepaths"""

    ddos: list[DDO]
    """List of paths to the DDOs"""

    # Store the type explicitly to avoid issues
    _type: Type[T] = field(repr=False)

    secret: str | None = None
    """Shh it's a secret"""

    def __post_init__(self) -> None:
        # Ensure '_type' is set correctly

        if not hasattr(self._type, "__dataclass_fields__"):
            raise TypeError(f"{self._type} is not a dataclass type")

    @cached_property
    def input_parameters(self) -> T:
        """Read the input parameters and return them in an instance of the dataclass T"""
        with open(config.path_algorithm_custom_parameters, "r") as f:
            return load_dataclass(f.read(), self._type)
