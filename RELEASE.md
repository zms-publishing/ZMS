# How to make a new ZMS release (PyPI and GitHub)

* update version.txt to the desired version. Remember that only the three first elements of the version are used.
* create a release build with `python setup.py sdist`
* test upload to testpypi via `twine upload --repository-url https://test.pypi.org/legacy/ dist/$name_of_release_file`
* check release on https://test.pypi.org/project/ZMS/
* If content, tag and upload release to real pypi via `twine upload dist/$name_of_release_file`
* update version.txt and add `dev` suffix to the patch version
* `git push --tags` all changes to GitHub
* Create a release from the tag on GitHub

See [the Twine](https://twine.readthedocs.io/en/latest/)
and [the TestPyPi](https://packaging.python.org/guides/using-testpypi/) documentation for details.
