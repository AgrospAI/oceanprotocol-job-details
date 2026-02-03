# mypy: disable-error-code=explicit-any
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, JsonValue


class Credential(BaseModel):
    type: str
    values: list[str]


class Credentials(BaseModel):
    allow: list[Credential]
    deny: list[Credential]


class DockerContainer(BaseModel):
    image: str
    tag: str
    entrypoint: str


class Algorithm(BaseModel):
    container: DockerContainer
    language: str
    version: str
    consumerParameters: JsonValue


class Metadata(BaseModel):
    description: str
    name: str
    type: str
    author: str
    license: str
    algorithm: Optional[Algorithm] = None
    tags: Optional[list[str]] = None
    created: Optional[str] = None
    updated: Optional[str] = None
    copyrightHolder: Optional[str] = None
    links: Optional[list[str]] = None
    contentLanguage: Optional[str] = None
    categories: Optional[list[str]] = None


class ConsumerParameters(BaseModel):
    name: str
    type: str
    label: str
    required: bool
    description: str
    default: str
    option: Optional[list[str]] = None


class Service(BaseModel):
    id: str
    type: str
    timeout: int
    files: str
    datatokenAddress: str
    serviceEndpoint: str
    additionalInformation: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None


class Event(BaseModel):
    tx: str
    block: int
    from_: str = Field(alias="from")
    contract: str
    datetime: str

    model_config = ConfigDict(populate_by_name=True)


class NFT(BaseModel):
    address: str
    name: str
    symbol: str
    state: int
    tokenURI: str
    owner: str
    created: str


class DataToken(BaseModel):
    address: str
    name: str
    symbol: str
    serviceId: str


class Price(BaseModel):
    value: int


class Stats(BaseModel):
    allocated: int
    orders: int
    price: Price


class Purgatory(BaseModel):
    state: bool


class DDO(BaseModel):
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
    purgatory: Purgatory

    model_config = ConfigDict(populate_by_name=True)
