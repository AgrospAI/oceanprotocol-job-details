# Build steps


## Upgrade dependencies and build package

```PowerShell
python -m pip install --upgrade build twine 
python -m build
```

## Upload to repository

Upload the package to the `pypi` repository, or `testpypi` for testing purposes.

```Powershell
python -m twine upload --repository pypi dist/*
python -m twine upload --repository testpypi dist/*
```
