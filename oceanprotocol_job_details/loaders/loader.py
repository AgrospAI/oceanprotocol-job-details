from abc import ABC, abstractmethod
from typing import Generic, TypeVar


T = TypeVar("T")


class Loader(
    ABC,
    Generic[T],
):
    @abstractmethod
    def load(
        self,
        *args,
        **kwargs,
    ) -> T:
        """Load an instance of the given type"""
        pass


del T
