0. Make sure all changes are live and that Travis is green
0. Update README.md with release notes
0. Update setup.py for the new version number
0. `pip install -U twine wheel`
0. `python setup.py sdist`
0. `python setup.py bdist_wheel`
0. For each file in `dist/`: `gpg2 --detach-sign -a <filename>`
0. `twine upload dist/*`
0. Commit everything for the release
0. `git tag -a vN.N.N`
0. `git push git@github.com:brettcannon/caniusepython3.git --tags`
