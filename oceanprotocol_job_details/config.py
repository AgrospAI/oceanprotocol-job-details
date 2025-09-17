from dataclasses import dataclass, fields
from logging import getLogger
from pathlib import Path

logger = getLogger(__name__)


@dataclass
class Config:
    """Configuration class for the Ocean Protocol Job Details"""

    path_data: Path = Path("/data")
    """The path to the data directory"""

    path_inputs: Path = path_data / "inputs"
    """The path to the inputs directory"""

    path_ddos: Path = path_data / "ddos"
    """The path to the DDOs directory"""

    path_outputs: Path = path_data / "outputs"
    """The path to the outputs directory"""

    path_logs: Path = path_data / "logs"
    """The path to the logs directory"""

    path_algorithm_custom_parameters: Path = path_inputs / "algoCustomData.json"
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
        current_value = getattr(config, field.name)
        if not isinstance(current_value, Path):
            raise ValueError(f"Field {field.name} is n|ot a Path")

        rel_path = Path(current_value).relative_to("/data")
        object.__setattr__(config, field.name, base / rel_path)


__all__ = ["config"]
