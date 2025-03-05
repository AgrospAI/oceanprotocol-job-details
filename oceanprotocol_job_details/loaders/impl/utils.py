from logging import WARNING, getLogger
from typing import Callable, TypeVar

logger = getLogger(__name__)
R = TypeVar("R")


def do(
    function: Callable[[], R],
    exception: Exception,
    *,
    log_level=WARNING,
    default: R = None,
) -> R:
    """Executes a function and logs the exception if it fails

    :param function: function to call
    :type function: Callable
    :param exception: exception to catch
    :type exception: Exception
    :param log_level: logging level to use
    :type log_level: int
    :return: result of the function and if it was successful
    :rtype: R
    """

    try:
        return function()
    except exception as e:
        logger.log(log_level, e)
        return default
