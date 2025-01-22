# Build steps


## Upgrade dependencies and build package

```PowerShell
python -m pip install --upgrade build twine 
python -m build
```

## Upload to repository

Upload the package to the `pypi` repository (default when empty), or `testpypi` for testing purposes.

```Powershell
python -m twine upload dist/*
python -m twine upload --repository testpypi dist/*
```

## Run tests

After developing a feature or fixing things, run the tests with

```PowerShell
poetry run pytest
```