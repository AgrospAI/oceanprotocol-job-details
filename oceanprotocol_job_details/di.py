from typing import Generic, TypeVar
from dependency_injector import containers, providers
from pydantic import BaseModel

from oceanprotocol_job_details.loaders.impl.ddo import DDOLoader
from oceanprotocol_job_details.loaders.impl.files import FilesLoader
from oceanprotocol_job_details.loaders.impl.job_details import JobDetailsLoader
from oceanprotocol_job_details.domain import Paths


InputParametersT = TypeVar("InputParametersT", BaseModel, None)


class Container(containers.DeclarativeContainer, Generic[InputParametersT]):
    config = providers.Configuration()

    paths = providers.Singleton(Paths, base_dir=config.base_dir)

    file_loader = providers.Singleton(
        FilesLoader,
        dids=config.dids,
        transformation_did=config.transformation_did,
        paths=paths,
        logger=config.logger,
    )

    files = providers.Factory(lambda loader: loader.load(), loader=file_loader)
    ddo_loader = providers.Factory(DDOLoader, files=files)
    ddos = providers.Factory(lambda loader: loader.load(), loader=ddo_loader)

    job_details_loader: providers.Factory[JobDetailsLoader[InputParametersT]] = (
        providers.Factory(
            JobDetailsLoader,
            files=files,
            secret=config.secret,
            paths=paths,
            ddos=ddos,
        )
    )
