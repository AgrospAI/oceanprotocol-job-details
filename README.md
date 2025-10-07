A Python package to get details from OceanProtocol jobs

---

## Installation

```
pip install oceanprotocol-job-details
```

## Usage 

As a simple library, we only need to import `JobDetails` and load it, it will:

1. Fetch the needed parameters to populate the `JobDetails` instance from the environment variables or use the passed values to the `load()` method.
1. Look for the files corresponding to the passed DIDs in the filesystem according to the [Ocean Protocol Structure](#oceanprotocol-structure) and load them into the `JobDetails` instance.


### Minimal Example

```python
from oceanprotocol_job_details import JobDetails

job_details = JobDetails.load()
```

### Custom Input Parameters

If our algorithm has custom input parameters and we want to load them into our algorithm, we can do it as follows:

```python
from dataclasses import dataclass
from oceanprotocol_job_details import JobDetails


@dataclass
class InputParameters:
    foobar: str


job_details = JobDetails[InputParameters].load(InputParameters)

# Usage
job_details.input_parameters.foobar
```

```python
from dataclasses import dataclass
from oceanprotocol_job_details import JobDetails


@dataclass
class Foo:
    bar: str


@dataclass
class InputParameters:
    # Allows for nested types
    foo: Foo


job_details = JobDetails[InputParameters].load(InputParameters)

# Usage
job_details.input_parameters.foo.bar
```

The values to fill the custom `InputParameters` will be parsed from the `algoCustomData.json` located next to the input data directories. 

## OceanProtocol Structure

```bash
data        # Root /data directory
├── ddos    # Contains the loaded dataset's DDO
│   ├── 17feb...e42 # DDO file
│   └── ... # One DDO per loaded dataset
├── inputs  # Datasets dir
│   ├── 17feb...e42 # Dir holding the data of its name DID, contains files named 0..X
│   │   └── 0 # Data file
│   └── algoCustomData.json # Custom algorithm input data
├── logs    # Algorithm output logs dir
└── outputs # Algorithm output files dir
```

> **_Note:_** Even though it's possible that the algorithm is passed multiple datasets, right now the implementation only allows to use **one dataset** per algorithm execution, so **normally** the executing job will only have **one ddo**, **one dir** inside inputs, and **one data file** named `0`.