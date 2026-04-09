from typing import Generic, TypeVar

from dependency_injector import containers, providers
from pydantic import BaseModel

from oceanprotocol_job_details.domain import DDOMetadata, Files, Paths
from oceanprotocol_job_details.loaders import Loader
from oceanprotocol_job_details.ocean import JobDetails
from oceanprotocol_job_details.plugins import inject

InputParametersT = TypeVar("InputParametersT", bound=BaseModel | None)


class Container(containers.DeclarativeContainer, Generic[InputParametersT]):
    config = providers.Configuration()

    paths = providers.Singleton(
        Paths,
        base_dir=config.base_dir,
    )

    files = providers.Factory(
        lambda dids, transformation_did, paths, logger: inject(
            Loader[Files],
            "files",
            paths,
            logger,
            dids,
            transformation_did,
        ).load(),
        dids=config.dids,
        transformation_did=config.transformation_did,
        paths=paths,
        logger=config.logger,
    )

    metadata = providers.Factory(
        lambda files: inject(Loader[DDOMetadata], "ddo", files=files).load(),
        files=files,
    )

    job_details_loader = providers.Factory(
        lambda files, secret, paths, metadata, **kwargs: inject(
            Loader[JobDetails[InputParametersT]],
            "jobdetails",
            files,
            secret,
            paths,
            metadata,
            **kwargs,
        ),
        files=files,
        secret=config.secret,
        paths=paths,
        metadata=metadata,
    )
