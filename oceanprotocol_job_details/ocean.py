from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field
from functools import cached_property
from pathlib import Path
from typing import (
    Any,
    Generator,
    Generic,
    Iterator,
    Optional,
    Sequence,
    Type,
    TypeVar,
    final,
)

import orjson
from dataclasses_json import config as dc_config
from dataclasses_json import dataclass_json

from oceanprotocol_job_details.di import Container
from oceanprotocol_job_details.paths import Paths

T = TypeVar("T")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(threadName)s] [%(levelname)s]  %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


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
class DockerContainer:
    image: str
    tag: str
    entrypoint: str


@dataclass_json
@dataclass
class Algorithm:  # type: ignore
    container: DockerContainer
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


@dataclass(frozen=True)
class DIDPaths:
    did: str
    ddo: Path
    input_files: Sequence[Path]

    def __post_init__(self) -> None:
        assert self.ddo.exists(), f"DDO {self.ddo} does not exist"
        for input_file in self.input_files:
            assert input_file.exists(), f"File {input_file} does not exist"

    def __len__(self) -> int:
        return len(self.input_files)


@dataclass(frozen=True)
class Files:
    _files: Sequence[DIDPaths]

    @property
    def files(self) -> Sequence[DIDPaths]:
        return self._files

    def __getitem__(self, index: int) -> DIDPaths:
        return self.files[index]

    def __iter__(self) -> Iterator[DIDPaths]:
        return iter(self.files)

    def __len__(self) -> int:
        return len(self.files)


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
@dataclass
class _EmptyJobDetails: ...


@final
@dataclass_json
@dataclass(frozen=True)
class JobDetails(Generic[T]):
    files: Files
    """The input filepaths"""

    ddos: list[DDO]
    """list of paths to the DDOs"""

    paths: Paths
    """Configuration paths"""

    # Store the type explicitly to avoid issues
    _type: Type[T] = field(repr=False)

    secret: str | None = None
    """Shh it's a secret"""

    def __post_init__(self) -> None:
        if not hasattr(self._type, "__dataclass_fields__"):
            raise TypeError(f"{self._type} is not a dataclass type")

    def next_path(self) -> Generator[tuple[int, Path], None, None]:
        for idx, did_files in enumerate(self.files):
            for file in did_files.input_files:
                yield (idx, file)

    @cached_property
    def input_parameters(self) -> T:
        """Read the input parameters and return them in an instance of the dataclass T"""

        with open(self.paths.algorithm_custom_parameters, "r") as f:
            raw = f.read().strip()
            if not raw:
                raise ValueError(
                    f"Custom parameters file {self.paths.algorithm_custom_parameters} is empty"
                )
            try:
                parsed = _normalize_json(orjson.loads(raw))
                return dataclass_json(self._type).from_dict(parsed)  # type: ignore
            except Exception as e:
                raise ValueError(
                    f"Failed to parse input paramers into {self._type.__name__}: {e}\n"
                    f"Raw content: {raw}"
                ) from e

    @classmethod
    def load(
        cls,
        _type: Type[T] | None = None,
        *,
        base_dir: str | None = None,
        dids: str | None = None,
        transformation_did: str | None = None,
        secret: str | None = None,
    ) -> JobDetails[T]:
        """Load a JobDetails instance that holds the runtime details.

        Loading it will check the following:
        1. That the needed environment variables are set.
        1. That the ocean protocol contains the needed data based on the passed environment variables.

        Those needed environment variables are:
        - BASE_DIR: Base directory to read the data from, parent of the ddos, inputs, outputs and logs directories.
        - DIDS: The DIDs of the inputs
        - TRANSFORMATION_DID: The DID of the transformation algorithm
        - SECRET (optional): A really secret secret

        """

        if _type is None:
            _type = _EmptyJobDetails

        container = Container()
        container.config.from_dict(
            {
                "base_dir": base_dir or os.environ.get("BASE_DIR"),
                "dids": dids or os.environ.get("DIDS"),
                "transformation_did": transformation_did
                or os.environ.get("TRANSFORMATION_DID"),
                "secret": secret or os.environ.get("SECRET"),
            }
        )

        return container.job_details_loader(_type=_type).load()
