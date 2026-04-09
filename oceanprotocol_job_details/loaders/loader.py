from abc import ABC, abstractmethod
from typing import Generic, TypeVar

T = TypeVar("T", covariant=True)


class Loader(ABC, Generic[T]):
    @abstractmethod
    def load(self) -> T:
        """Load an instance of the given type"""
