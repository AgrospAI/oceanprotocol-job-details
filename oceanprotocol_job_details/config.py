from dataclasses import dataclass


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

__all__ = ["config"]
