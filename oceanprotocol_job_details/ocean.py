from dataclasses import Field, dataclass
from datetime import datetime
from functools import cached_property
from typing import Annotated, Any, Generic, List, Optional, TypeVar

from pydantic import BaseModel, HttpUrl

from oceanprotocol_job_details.config import config
from oceanprotocol_job_details.loaders.impl.files import Files
from oceanprotocol_job_details.utils import load_dataclass


class Credential(BaseModel):  # type: ignore
    type: Annotated[str, Field(frozen=True)]
    values: Annotated[List[str], Field(frozen=True)]


class Credentials(BaseModel):  # type: ignore
    allow: Optional[Annotated[List[Credential], Field(frozen=True)]] = []
    deny: Optional[Annotated[List[Credential], Field(frozen=True)]] = []


class Metadata(BaseModel):  # type: ignore
    """Base class for the Metadata structure"""

    description: Annotated[str, Field(frozen=True)]
    name: Annotated[str, Field(frozen=True)]
    type: Annotated[str, Field(frozen=True)]
    author: Annotated[str, Field(frozen=True)]
    license: Annotated[str, Field(frozen=True)]

    algorithm: str  # TODO: Add Algorithm class
    tags: Optional[Annotated[List[str], Field(frozen=True)]] = None
    created: Optional[Annotated[datetime, Field(frozen=True)]] = None
    updated: Optional[Annotated[datetime, Field(frozen=True)]] = None
    copyrightHolder: Optional[Annotated[str, Field(frozen=True)]] = None
    links: Optional[Annotated[List[HttpUrl], Field(frozen=True)]] = None
    contentLanguage: Optional[Annotated[str, Field(frozen=True)]] = None
    categories: Optional[Annotated[List[str], Field(frozen=True)]] = None


class ConsumerParameters(BaseModel):  # type: ignore
    """Base class for the ConsumerParameters structure"""

    name: Annotated[str, Field(frozen=True)]
    type: Annotated[str, Field(frozen=True)]
    label: Annotated[str, Field(frozen=True)]
    required: Annotated[bool, Field(frozen=True)]
    description: Annotated[str, Field(frozen=True)]
    default: Annotated[str, Field(frozen=True)]

    option: Annotated[Optional[List[str]], Field(frozen=True)] = None


class Service(BaseModel):  # type: ignore
    """Base class for the Service structure"""

    id: Annotated[str, Field(frozen=True)]
    type: Annotated[str, Field(frozen=True)]
    timeout: Annotated[int, Field(frozen=True)]
    files: Annotated[str, Field(frozen=True)]
    datatokenAddress: Annotated[str, Field(frozen=True)]
    serviceEndpoint: Annotated[HttpUrl, Field(frozen=True)]

    consumerParameters: ConsumerParameters
    additionalInformation: str
    name: Optional[Annotated[str, Field(frozen=True)]] = None
    description: Optional[Annotated[str, Field(frozen=True)]] = None


class Event(BaseModel):  # type: ignore
    tx: Annotated[str, Field(frozen=True)]
    block: Annotated[int, Field(frozen=True)]
    from_: Annotated[str, Field(frozen=True, alias="from")]
    contract: Annotated[str, Field(frozen=True)]
    datetime: Annotated[datetime, Field(frozen=True)]


class NFT(BaseModel):  # type: ignore
    address: Annotated[str, Field(frozen=True)]
    name: Annotated[str, Field(frozen=True)]
    symbol: Annotated[str, Field(frozen=True)]
    state: Annotated[int, Field(frozen=True)]
    tokenURI: Annotated[HttpUrl, Field(frozen=True)]
    owner: Annotated[str, Field(frozen=True)]
    created: Annotated[datetime, Field(frozen=True)]


class DataToken(BaseModel):  # type: ignore
    address: Annotated[str, Field(frozen=True)]
    name: Annotated[str, Field(frozen=True)]
    symbol: Annotated[str, Field(frozen=True)]
    serviceId: Annotated[datetime, Field(frozen=True)]


class Price(BaseModel):  # type: ignore
    value: Annotated[int, Field(frozen=True)]


class Stats(BaseModel):  # type: ignore
    allocated: Annotated[int, Field(frozen=True)]
    orders: Annotated[int, Field(frozen=True)]
    price: Annotated[Price, Field(frozen=True)]


class DDO(BaseModel):  # type: ignore
    """DDO structure in Ocean Protocol"""

    id: Annotated[str, Field(frozen=True)]
    context: Annotated[List[str], Field(frozen=True, alias="@context")]
    nftAddress: Annotated[str, Field(frozen=True)]
    chainId: Annotated[int, Field(frozen=True)]
    version: Annotated[str, Field(frozen=True)]
    metadata: Annotated[Metadata, Field(frozen=True)]
    services: Annotated[List[Service], Field(frozen=True)]
    credentials: Annotated[Credentials, Field(frozen=True)]
    event: Annotated[Event, Field(frozen=True)]
    nft: Annotated[NFT, Field(frozen=True)]
    datatokens: Annotated[List[DataToken], Field(frozen=True)]
    stats: Annotated[Stats, Field(frozen=True)]


T = TypeVar("T")


@dataclass(frozen=True)
class JobDetails(Generic[T]):

    files: Files
    """The input filepaths"""

    secret: Optional[str] = None
    """Shh it's a secret"""

    @cached_property
    def input_parameters(self) -> T:
        """Read the input parameters and return them in an instance of the dataclass T"""
        with open(config.path_algorithm_custom_parameters, "r") as f:
            return load_dataclass(f.read(), T)  # type: ignore
