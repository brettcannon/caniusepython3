0. Make sure all changes are live and that Travis is green
0. Delete all packaging-related directories(including `dist/`)
0. Verify there are no stale overrides
0. Update README.md with release notes
0. Update setup.py for the new version number
0. `python3 -m pip install --upgrade setuptools twine wheel`
0. `python3 setup.py sdist`
0. `python3 setup.py bdist_wheel`
0. `python3 -m twine upload dist/*`
0. Commit everything for the release
0. `git push`
0. Create a [release on GitHub](https://github.com/brettcannon/caniusepython3/releases)
