from dataclasses import dataclass, field, fields
from logging import getLogger
from typing import Any, Mapping, Optional, Type, TypeVar, get_type_hints

import orjson
from pydantic import BaseModel

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


def load_dataclass(
    data: str,
    cls: Type[T],
) -> T:
    """Map a dictionary to a dataclass object, using the default values when missing

    :param data: original data to get the item from
    :type data: str
    :param cls: class to instantiate from the data
    :type cls: Type[T]
    :raises KeyError: if any member is missing and no default is provided
    :return: value of the key
    :rtype: T
    :raises: orjson.JSONDecodeError: if the data cannot be decoded
    :raises: KeyError: if the value is missing and no default is provided
    """

    if not hasattr(cls, "__dataclass_fields__"):
        raise TypeError(f"{cls} is not a dataclass type")

    try:
        value = orjson.loads(data)
    except orjson.JSONDecodeError as e:
        logger.error(f"Error trying to decode JSON {data}: {e}")
        raise e

    # Get fields metadata
    cls_fields = {f.name: f for f in fields(cls)}  # type: ignore

    # Ensure the fields are required, otherwise use defaults
    ini_fields = {}
    for name, f in cls_fields.items():
        if name in value:
            ini_fields[name] = value.get(name)
        else:
            ini_fields[name] = f.default
            logger.info(
                f"Missing field {name} in {cls.__name__}, using default value {f.default}"
            )

    return cls(**ini_fields)


def pydantic_to_dataclass(pydantic_model: Type[BaseModel], values: dict = None) -> Any:  # type: ignore
    """Convert a Pydantic model to a dataclass.

    :param pydantic_model: Pydantic model to convert
    :type pydantic_model: Type[BaseModel]
    :param values: Optional dictionary to populate the dataclass with, defaults to None
    :type values: dict, optional
    :return: Dataclass instance
    :rtype: Any
    """

    model_type = type(pydantic_model)
    model_fields = get_type_hints(model_type)
    values = values or {}

    @dataclass
    class DynamicDataclass:
        pass

    # Populate the dataclass with fields
    for field_name, _ in model_fields.items():
        value = values.get(field_name, getattr(pydantic_model, field_name))
        setattr(DynamicDataclass, field_name, field(default=value))

    # Create an instance of the dataclass with field values
    return DynamicDataclass()
