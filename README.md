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

### Advanced Usage (not recommended)

If instead of the environment variables, we want to use another kind of mapping, can pass it as a parameter and it will work as long as it has the same key values (Can be implemented in a more generic way, but there is no need right now).

```Python
from oceanprotocol_job_details.job_details import OceanProtocolJobDetails
from oceanprotocol_job_details.loaders.impl.environment import Keys

# Fill in with values that will be used instead of env
custom_mapper = {
    Keys.ALGORITHM: " ... ",
    Keys.DIDS: " ... ",
    Keys.ROOT: " ... ",
    Keys.SECRET: " ... ",
}

job_details = OceanProtocolJobDetails(mapper=custom_mapper).load()
```
