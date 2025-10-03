A Python package to get details from OceanProtocol jobs

---

## Installation

```
pip install oceanprotocol-job-details
```

## Usage 

As a simple library, we only need to import the main object and use it once:

```Python
from oceanprotocol_job_details import JobDetails

# Having no algorithm input parameters
job_details = JobDetails.load()

```

If our algorithm has custom input parameters and we want to load them into our algorithm, we can do it as follows:

```Python

from dataclasses import dataclass
from oceanprotocol_job_details import JobDetails


@dataclass
class InputParameters:
    name: str
    age: int


job_details: JobDetails[InputParameters] = JobDetails.load(InputParameters)

# Usage (is type hinted)
job_details.input_parameters.name
job_details.input_parameters.age

```

Assumes the directory structure of OceanProtocol algorithms.

### Core functionalities

Given the Ocean Protocol job details structure, parses the passed algorithm parameters into an object to use in your algorithms.

1. Input parameter JSON parsing and validation
1. Metadata and service extraction from the directory structure.
