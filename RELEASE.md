# How to make a new ZMS release (PyPI and GitHub)

* update `Products/zms/version.txt` to the desired semantic version (for example `6.0.0`).
* create a release build with `python -m build` (creates both sdist and wheel from `pyproject.toml`).
* verify package metadata with `python -m twine check dist/*`.
* test upload to testpypi via `python -m twine upload --verbose --repository-url https://test.pypi.org/legacy/ dist/*`
* check release on https://test.pypi.org/project/ZMS/
* If content, tag and upload release to real pypi via `python -m twine upload dist/*`
* update `Products/zms/version.txt` and add `dev` suffix to the patch version
* `git push --tags` all changes to GitHub
* Create a release from the tag on GitHub

## Publish to PyPI via GitHub Actions

The repository contains the workflow `.github/workflows/pypi_publish.yml`.
It builds the package and publishes it to PyPI with
`pypa/gh-action-pypi-publish@release/v1` using GitHub OIDC trusted publishing
(no PyPI API token in repository secrets).

### Workflow triggers

Publishing is triggered by one of the following events:

* release published
* tag push matching `v*` (for example `v6.0.0`) or `*.*.*` (for example `6.0.0`)
* manual run via `workflow_dispatch`

### One-time prerequisites

1. In PyPI project `ZMS`, configure a Trusted Publisher for this GitHub repository and the workflow file `.github/workflows/pypi_publish.yml`.
2. Ensure the GitHub environment `pypi` exists in the repository settings.
3. If environment protection rules are enabled, grant release maintainers permission to approve the publish job.

### Recommended release flow

1. Update `Products/zms/version.txt` to the final release version and commit.
2. Create and push a release tag (recommended format `vX.Y.Z`):

	`git tag -a vX.Y.Z -m "Release X.Y.Z"`

	`git push origin vX.Y.Z`

3. Wait for the GitHub Action `Publish Python package to PyPI` to finish successfully.
4. Verify the uploaded artifacts in the workflow run (`dist/` contains wheel and sdist).
5. Verify the published package on https://pypi.org/project/ZMS/.

### Manual publish fallback

If needed, start the workflow manually in the Actions tab (`workflow_dispatch`).
Use this only for an intended release commit/tag.

See [the Twine](https://twine.readthedocs.io/en/latest/)
and [the TestPyPi](https://packaging.python.org/guides/using-testpypi/) documentation for details.
