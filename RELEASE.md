# How to make a new ZMS release (PyPI and GitHub)

* update `Products/zms/version.txt` to the desired semantic version (for example `5.2.1`).
* create a release build with `python -m build` (creates both sdist and wheel from `pyproject.toml`).
* verify package metadata with `python -m twine check dist/*`.
* test upload to testpypi via `python -m twine upload --repository-url https://test.pypi.org/legacy/ dist/*`
* check release on https://test.pypi.org/project/ZMS/
* If content, tag and upload release to real pypi via `python -m twine upload dist/*`
* update `Products/zms/version.txt` and add `dev` suffix to the patch version
* `git push --tags` all changes to GitHub
* Create a release from the tag on GitHub

See [the Twine](https://twine.readthedocs.io/en/latest/)
and [the TestPyPi](https://packaging.python.org/guides/using-testpypi/) documentation for details.
