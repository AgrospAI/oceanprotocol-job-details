# mypy: disable-error-code=explicit-any
from dataclasses import InitVar, dataclass, field
from pathlib import Path
from typing import Generator, List, Optional, Sequence, TypeAlias, TypeVar

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


@dataclass(frozen=True)
class DIDPaths:
    did: str
    ddo: Path = field(repr=False)

    files: InitVar[Generator[Path, None, None]]

    _input: List[Path] = field(init=False, repr=False)

    def __post_init__(self, files: Generator[Path, None, None]) -> None:
        assert self.ddo.exists(), f"DDO {self.ddo} does not exist"

        object.__setattr__(self, "_input", list(files))

    @property
    def input_files(self) -> List[Path]:
        return self._input

    def __len__(self) -> int:
        return len(self._input)


Files: TypeAlias = Sequence[DIDPaths]


@dataclass(frozen=True)
class Paths:
    """Configuration class for the Ocean Protocol Job Details"""

    base_dir: InitVar[Path | None] = None

    _base: Path = field(init=False, repr=False)

    def __post_init__(self, base_dir: Path | None) -> None:
        object.__setattr__(self, "_base", base_dir if base_dir else Path("/data"))

    @property
    def data(self) -> Path:
        return self._base

    @property
    def inputs(self) -> Path:
        return self.data / "inputs"

    @property
    def ddos(self) -> Path:
        return self.data / "ddos"

    @property
    def outputs(self) -> Path:
        return self.data / "outputs"

    @property
    def logs(self) -> Path:
        return self.data / "logs"

    @property
    def algorithm_custom_parameters(self) -> Path:
        return self.inputs / "algoCustomData.json"
