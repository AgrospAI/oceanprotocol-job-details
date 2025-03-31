from logging import getLogger
from typing import Mapping, Optional, TypeVar

T = TypeVar("T")
logger = getLogger(__name__)


def get(
    map: Mapping[str, T],
    key: str,
    default: Optional[T] = None,
) -> T | None:
    """Get the value of a key from a dictionary, if not found return the default value if given, otherwise raise a KeyError

    :param map: original map to get the item from
    :type map: Mapping[str, T]
    :param key: key to get the value from
    :type key: str
    :param default: default value if missing, defaults to None
    :type default: Optional[T], optional
    :raises KeyError: if the value is missing and no default is provided
    :return: value of the key
    :rtype: T
    """

    if key in map.keys():
        return map.get(key)

    if default is None:
        raise KeyError(f"Key {key} not found")

    logger.info(f"Key {key} not found, returning default value {default}")
    return default
