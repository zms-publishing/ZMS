# How to make a new ZMS release (PyPI and GitHub)

* update `Products/zms/version.txt` to the desired semantic version (for example `6.3.0`).
* create a release build with `python -m build` (creates both sdist and wheel from `pyproject.toml`).
* verify package metadata with `python -m twine check dist/*`.
* test upload to testpypi via `python -m twine upload --verbose --repository-url https://test.pypi.org/legacy/ dist/*`
* check release on https://test.pypi.org/project/ZMS/
* If content, tag and upload release to real pypi via `python -m twine upload dist/*`
* update `Products/zms/version.txt` and add `dev` suffix to the patch version
* `git push --tags` all changes to GitHub
* Create a release from the tag on GitHub

## Publish to PyPI via GitHub Actions

Two workflows build the source distribution and wheel, check them with Twine,
then publish using GitHub OIDC trusted publishing (no PyPI API token is stored in GitHub):

| Workflow | Destination | Automatic trigger | GitHub environment |
|---|---|---|---|
| `.github/workflows/pypi_publish_test.yml` | [TestPyPI](https://test.pypi.org/project/ZMS/) | A prerelease event | `pypitest` |
| `.github/workflows/pypi_publish.yml` | [PyPI](https://pypi.org/project/ZMS/) | A published release | `pypi` |

Both workflows can also be started manually with workflow_dispatch`. The tag-push trigger shown as comments in the production workflow is disabled.

### One-time setup

1. Configure a Trusted Publisher for this GitHub repository on both PyPI and
   TestPyPI. Register the corresponding workflow filename on each service:
   `.github/workflows/pypi_publish.yml` for PyPI and
   `.github/workflows/pypi_publish_test.yml` for TestPyPI.
2. Ensure the GitHub environments `pypi` and `pypitest` exist in repository
   settings. Configure any desired environment protection/approval rules.
3. If publishing requires environment approval, ensure the release maintainers
   are allowed to approve the respective deployment.

### Publish the current check-in

1. Push the intended check-in to GitHub. In the Actions UI, choose the branch
   that points to that check-in when manually starting a workflow. A manual run
   builds the selected branch's code; it does not select a commit by hash.
2. First test it on TestPyPI:
   - Open **Actions** and select **Publish Python package to TestPyPI**.
   - Choose **Run workflow**, select the intended branch, then start the run.
   - Wait for both the build and publish jobs to succeed. The build job runs
     `python -m build` and `python -m twine check dist/*`.
   - Verify the package/version on
     [TestPyPI](https://test.pypi.org/project/ZMS/).
3. If the test is successful and this is an intended public release, open
   **Actions**, select **Publish Python package to PyPI**, choose **Run
   workflow**, select the same branch, and start the run. This uploads to the
   real PyPI; verify the result at
   [PyPI](https://pypi.org/project/ZMS/).
4. Alternatively, publishing a GitHub Release triggers the production workflow.
   Use a final release (not a prerelease) for this route. Do not rely on a
   prerelease as a safety barrier: the production workflow listens for the
   `published` release event, which can also be emitted when a draft release is
   published.

The package version is read from `Products/zms/version.txt`; the `+...`
suffix, if present, is stripped when building the package. For example,
`6.3.0+6ec0d96` produces version `6.3.0`. PyPI does not allow overwriting an
already published version, so increment the version before publishing if that
version is already present on the destination.

Starting the TestPyPI workflow is not a production release. The production
workflow publishes to PyPI and should only be run after confirming the version,
branch, build, and TestPyPI result.

## References:

* [Twine](https://twine.readthedocs.io/en/latest/)
* [TestPyPi](https://packaging.python.org/guides/using-testpypi/)
* [PyPI-Project-Naming](https://github.com/zms-publishing/ZMS/pull/495)

