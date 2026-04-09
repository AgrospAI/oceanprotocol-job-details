from typing import TypeVar

from typing_extensions import override

from oceanprotocol_job_details.loaders.loader import Loader

T = TypeVar("T")


class InputLoader(Loader[T]):
    def __init__(self, supported: list[str]) -> None:
        self.supported = supported

    @override
    def load(self) -> T:
        return super().load()
