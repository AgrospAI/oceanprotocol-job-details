A Python package to get details from OceanProtocol jobs

---

## Installation

```
pip install oceanprotocol-job-details
```

## Usage 

As a simple library, we only need to import the main object and use it once:

```Python
from oceanprotocol_job_details.job_details import OceanProtocolJobDetails

# Using default parameters
job_details = OceanProtocolJobDetails().load()
```

Assumes the following directory structure:
```
<ROOT_FOLDER>
└───data
    ├───ddos
    ├───inputs
    └───logs
```

### Core functionalities

Given the Ocean Protocol job details structure as in [https://github.com/GX4FM-Base-X/pontus-x-ontology](Pontus-X Ontology), parses the passed algorithm parameters into an object to use in your algorithms.

1. Parsing JSON
1. Validation
1. Metadata and service extraction


### Advanced Usage (not recommended)

If instead of the environment variables, we want to use another kind of mapping, can pass it as a parameter and it will work as long as it has the same key values (Can be implemented in a more generic way, but there is no need right now).

```Python
from oceanprotocol_job_details.job_details import OceanProtocolJobDetails
from oceanprotocol_job_details.loaders.impl.environment import Keys

# Fill in with values that will be used instead of env
custom_mapper = {
    Keys.ROOT_FOLDER: " ... ", # Use when you don't want the algorithm to take '/' as base Path
    Keys.ALGORITHM: " ... ",
    Keys.DIDS: " ... ",
    Keys.SECRET: " ... ",
}

job_details = OceanProtocolJobDetails(mapper=custom_mapper).load()
```


