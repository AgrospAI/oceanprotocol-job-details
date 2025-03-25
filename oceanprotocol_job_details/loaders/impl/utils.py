from logging import getLogger
from typing import Callable, Type, TypeVar

logger = getLogger(__name__)
R = TypeVar("R")


def do(
    function: Callable[[], R],
    exception: Type[Exception] = Exception,
    *,
    default: R | None = None,
    error: bool = False,
) -> R | None:
    """Executes a function and logs the exception if it fails

    :param function: function to call
    :type function: Callable
    :param exception: expected exception type to catch
    :type exception: Type[Exception]
    :param default: default value to return if the function fails
    :type default: R
    :param exc: if the exception should be raised
    :type exc: bool
    :return: result of the function and if it was successful
    :rtype: R
    """

    try:
        return function()
    except exception as e:
        if error:
            raise e
        logger.warning(e)
        return default


def execute_predicate(
    function: Callable[[], R],
    predicate: Callable[[], bool],
) -> R | bool:
    """Executes a function if the predicate is true"

    :param function: function to call
    :type function: Callable
    :param predicate: predicate to check
    :type predicate: Callable
    :return: result of the function and if it was successful
    :rtype: R | bool
    """

    return predicate() and function()
