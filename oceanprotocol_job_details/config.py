from dataclasses import dataclass, fields
from logging import getLogger
from pathlib import Path

logger = getLogger(__name__)


@dataclass
class Config:
    """Configuration class for the Ocean Protocol Job Details"""

    path_data: str = "/data"
    """The path to the data directory"""

    path_inputs: str = path_data + "/inputs"
    """The path to the inputs directory"""

    path_ddos: str = path_data + "/ddos"
    """The path to the DDOs directory"""

    path_outputs: str = path_data + "/outputs"
    """The path to the outputs directory"""

    path_logs: str = path_data + "/logs"
    """The path to the logs directory"""

    path_algorithm_custom_parameters: str = path_inputs + "/algoCustomData.json"
    """The path to the algorithm's custom parameters file"""


config = Config()


def update_config_from(base: Path) -> None:
    """Updates the configuration to use the new base path, ensures that the base path exists.

    Args:
        base (Path): The new base path to use.
    """

    logger.info(f"Updating config to use base path: {base}")

    base.mkdir(parents=True, exist_ok=True)

    for field in fields(config):
        default_value = field.default
        if default_value is None or not isinstance(default_value, Path):
            raise ValueError(f"Field {field.name} has no default value")

        object.__setattr__(config, field.name, str(base / default_value))


__all__ = ["config"]
