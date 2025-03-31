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

# Having no algorithm input parameters
job_details = OceanProtocolJobDetails().load()  # type: ignore

```

If our algorithm has custom input parameters and we want to load them into our algorithm, we can do it as follows:

```Python

from dataclasses import dataclass
from oceanprotocol_job_details.job_details import OceanProtocolJobDetails
from oceanprotocol_job_details.ocean import JobDetails

@dataclass
class Input:
    name: str
    age: int

job_details: JobDetails[Input] = OceanProtocolJobDetails(Input).load()

# Usage (is type hinted)
job_details.input_parameters.name
job_details.input_parameters.age

```

Assumes the following directory structure:
```
<ROOT_FOLDER>
└───data
    ├───ddos
    ├───transformation
    ├───inputs
    └───logs
```

### Core functionalities

Given the Ocean Protocol job details structure as in [https://github.com/GX4FM-Base-X/pontus-x-ontology](Pontus-X Ontology), parses the passed algorithm parameters into an object to use in your algorithms.

1. Parsing JSON
1. Validation
1. Metadata and service extraction
