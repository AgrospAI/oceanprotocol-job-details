from logging import WARNING, getLogger
from typing import Callable, TypeVar

logger = getLogger(__name__)
R = TypeVar("R")


def do(
    function: Callable[[], R],
    exception: Exception = Exception,
    *,
    log_level=WARNING,
    default: R = None,
    exc=False,
) -> R:
    """Executes a function and logs the exception if it fails

    :param function: function to call
    :type function: Callable
    :param exception: exception to catch
    :type exception: Exception
    :param log_level: logging level to use
    :type log_level: int
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
        logger.log(log_level, e)
        if exc:
            if isinstance(exc, Exception):
                raise exc from e
            raise e
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
