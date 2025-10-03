from dataclasses import dataclass
from logging import getLogger
from pathlib import Path

logger = getLogger(__name__)


@dataclass
class Paths:
    """Configuration class for the Ocean Protocol Job Details"""

    data: Path = Path("/data")
    """The path to the data directory"""

    inputs: Path = data / "inputs"
    """The path to the inputs directory"""

    ddos: Path = data / "ddos"
    """The path to the DDOs directory"""

    outputs: Path = data / "outputs"
    """The path to the outputs directory"""

    logs: Path = data / "logs"
    """The path to the logs directory"""

    algorithm_custom_parameters: Path = inputs / "algoCustomData.json"
    """The path to the algorithm's custom parameters file"""
