from dataclasses import dataclass, field
from functools import cached_property
from typing import Any, Generic, Optional, Type, TypeVar, final

import orjson

from dataclasses_json import config as dc_config
from dataclasses_json import dataclass_json

from oceanprotocol_job_details.config import config
from oceanprotocol_job_details.loaders.impl.files import Files

T = TypeVar("T")


@dataclass_json
@dataclass
class Credential:
    type: str
    values: list[str]


@dataclass_json
@dataclass
class Credentials:
    allow: list[Credential]
    deny: list[Credential]


@dataclass_json
@dataclass
class Container:
    image: str
    tag: str
    entrypoint: str


@dataclass_json
@dataclass
class Algorithm:  # type: ignore
    container: Container
    language: str
    version: str
    consumerParameters: Any  # type: ignore


@dataclass_json
@dataclass
class Metadata:
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


@dataclass_json
@dataclass
class ConsumerParameters:
    name: str
    type: str
    label: str
    required: bool
    description: str
    default: str
    option: Optional[list[str]] = None


@dataclass_json
@dataclass
class Service:
    id: str
    type: str
    timeout: int
    files: str
    datatokenAddress: str
    serviceEndpoint: str
    additionalInformation: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None


@dataclass_json
@dataclass
class Event:
    tx: str
    block: int
    from_: str = field(metadata=dc_config(field_name="from"))
    contract: str
    datetime: str


@dataclass_json
@dataclass
class NFT:
    address: str
    name: str
    symbol: str
    state: int
    tokenURI: str
    owner: str
    created: str


@dataclass_json
@dataclass
class DataToken:
    address: str
    name: str
    symbol: str
    serviceId: str


@dataclass_json
@dataclass
class Price:
    value: int


@dataclass_json
@dataclass
class Stats:
    allocated: int
    orders: int
    price: Price


@dataclass_json
@dataclass
class Purgatory:
    state: bool


@dataclass_json
@dataclass
class DDO:
    id: str
    context: list[str] = field(metadata=dc_config(field_name="@context"))
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


def _normalize_json(value):
    if isinstance(value, str):
        try:
            decoded = orjson.loads(value)
            return _normalize_json(decoded)  # recurse if nested again
        except orjson.JSONDecodeError:
            return value
    elif isinstance(value, dict):
        return {k: _normalize_json(v) for k, v in value.items()}
    elif isinstance(value, list):
        return [_normalize_json(v) for v in value]
    return value


@final
@dataclass_json
@dataclass(frozen=True)
class JobDetails(Generic[T]):
    files: Files
    """The input filepaths"""

    ddos: list[DDO]
    """list of paths to the DDOs"""

    # Store the type explicitly to avoid issues
    _type: Type[T] = field(repr=False)

    secret: str | None = None
    """Shh it's a secret"""

    def __post_init__(self) -> None:
        if not hasattr(self._type, "__dataclass_fields__"):
            raise TypeError(f"{self._type} is not a dataclass type")

    @cached_property
    def input_parameters(self) -> T:
        """Read the input parameters and return them in an instance of the dataclass T"""

        with open(config.path_algorithm_custom_parameters, "r") as f:
            raw = f.read().strip()
            if not raw:
                raise ValueError(
                    f"Custom parameters file {config.path_algorithm_custom_parameters} is empty"
                )
            try:
                parsed = _normalize_json(orjson.loads(raw))
                return dataclass_json(self._type).from_dict(parsed)  # type: ignore
            except Exception as e:
                raise ValueError(
                    f"Failed to parse input paramers into {self._type.__name__}: {e}\n"
                    f"Raw content: {raw}"
                ) from e
