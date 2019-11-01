1. Make sure all changes are live and that Travis is green
1. Delete all packaging-related directories(including `dist/`)
1. Verify there are no stale overrides
1. Update `README.md` with release notes
1. Update `setup.py` with the new version number
1. `python3 -m pip install --upgrade setuptools twine wheel`
1. `python3 setup.py sdist`
1. `python3 setup.py bdist_wheel`
1. `python3 -m twine check dist/*`
1. `python3 -m twine upload dist/*`
1. Commit everything from the release
1. `git push`
1. Create a [release on GitHub](https://github.com/brettcannon/caniusepython3/releases)
