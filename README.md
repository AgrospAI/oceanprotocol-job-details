A Python package to get details from OceanProtocol jobs

---

## Installation

```bash
pip install oceanprotocol-job-details
```

```bash
uv add oceanprotocol-job-details
```

## Usage

As a simple library, we only need to import `load_job_details` and run it. It will:

1. Fetch the needed parameters to populate the `JobDetails` instance from the environment variables or use the passed values to the function.
1. Look for the files corresponding to the passed DIDs in the filesystem according to the [Ocean Protocol Structure](#oceanprotocol-structure) and load them into the `JobDetails` instance.

### Minimal Example

```python
from oceanprotocol_job_details import load_job_details

class InputParameters(BaseModel): ...

job_details = load_job_details({}, InputParameters)
```

### Custom Input Parameters

If our algorithm has custom input parameters and we want to load them into our algorithm, we can do it as follows:

```python
from pydantic import BaseModel
from oceanprotocol_job_details import load_job_details


class Foo(BaseModel):
    bar: str


class InputParameters(BaseModel):
    # Allows for nested types
    foo: Foo


job_details = load_job_details({}, InputParameters)

# Usage
job_details.input_parameters.foo
job_details.input_parameters.foo.bar
```

The values to fill the custom `InputParameters` will be parsed from the `algoCustomData.json` located next to the input data directories.

### Iterating Input Files the clean way

```python
from oceanprotocol_job_details import load_job_details


job_details = load_job_details

for idx, file_path in job_details.inputs():
    ...

_, file_path = next(job_details.inputs())
```

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
