from dataclasses import Field
from datetime import datetime
from typing import Annotated, Any, List, Optional

from pydantic import BaseModel, HttpUrl

"""Base classes for the Ocean Protocol algorithm structure"""


class Credential:
    type: Annotated[str, Field(frozen=True)]
    values: Annotated[List[str], Field(frozen=True)]


class Credentials:
    allow: Optional[Annotated[List[Credential], Field(frozen=True)]] = []
    deny: Optional[Annotated[List[Credential], Field(frozen=True)]] = []


class Metadata(BaseModel):
    """Base class for the Metadata structure"""

    description: Annotated[str, Field(frozen=True)]
    name: Annotated[str, Field(frozen=True)]
    type: Annotated[str, Field(frozen=True)]
    author: Annotated[str, Field(frozen=True)]
    license: Annotated[str, Field(frozen=True)]

    algorithm: Any
    tags: Optional[Annotated[List[str], Field(frozen=True)]] = None
    created: Optional[Annotated[datetime, Field(frozen=True)]] = None
    updated: Optional[Annotated[datetime, Field(frozen=True)]] = None
    copyrightHolder: Optional[Annotated[str, Field(frozen=True)]] = None
    links: Optional[Annotated[List[HttpUrl], Field(frozen=True)]] = None
    contentLanguage: Optional[Annotated[str, Field(frozen=True)]] = None
    categories: Optional[Annotated[List[str], Field(frozen=True)]] = None


class Service(BaseModel):
    """Base class for the Service structure"""

    id: Annotated[str, Field(frozen=True)]
    type: Annotated[str, Field(frozen=True)]
    timeout: Annotated[int, Field(frozen=True)]
    files: Annotated[str, Field(frozen=True)]
    datatokenAddress: Annotated[str, Field(frozen=True)]
    serviceEndpoint: Annotated[HttpUrl, Field(frozen=True)]

    compute: Any
    consumerParameters: Any
    additionalInformation: Any
    name: Optional[Annotated[str, Field(frozen=True)]] = None
    description: Optional[Annotated[str, Field(frozen=True)]] = None


class DDO(BaseModel):
    """DDO structure in Ocean Protocol"""

    id: Annotated[str, Field(frozen=True)]
    context: Annotated[List[str], Field(frozen=True)]
    version: Annotated[str, Field(frozen=True)]
    chainId: Annotated[int, Field(frozen=True)]
    nftAddress: Annotated[str, Field(frozen=True)]
    metadata: Annotated[Metadata, Field(frozen=True)]
    services: Annotated[List[Service], Field(frozen=True)]

    credentials: Annotated[Optional[str], Field(frozen=True)] = None
