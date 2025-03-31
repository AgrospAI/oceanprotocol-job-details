from dataclasses import dataclass, field
from functools import cached_property
from typing import Generic, Optional, Type, TypeVar, final

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
class Metadata:
    description: str
    name: str
    type: str
    author: str
    license: str
    algorithm: Optional[str] = None  # TODO: Add Algorithm class
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
    # TODO: Inside Algorithm class
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
class SimpleDataToken:
    address: str
    name: str
    symbol: str


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
class AccessDetails:
    templateId: int
    publisherMarketOrderFee: str
    type: str
    addressOrId: str
    price: str
    isPurchasable: bool
    datatoken: SimpleDataToken


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
    accessDetails: AccessDetails


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
            return dataclass_json(self._type).from_json(f.read())  # type: ignore
