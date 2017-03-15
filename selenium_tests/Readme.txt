# How to run Selenium Acceptance Tests

## Setup

Geckodriver needs to be installed in the $PATH from: https://github.com/mozilla/geckodriver/releases

Install the testing requirements via:

    pip install -r selenium_tests/requirements.txt

The tests expect a running zope instance on http://localhost:8080 with login admin:admin

## Run them

To run all tests:

    python -m unittest discover -s selenium_tests -p '*test.py'

or

    pytest selenium_tests

`pytest` is used on the server (and has nice features) so it might be usefull locally too.

To run a specific test:

    python -m unittest selenium_tests.login_test.LoginTestCase.test_login

Here `selenium_tests.login_test.LoginTestCase` would run all tests in that class or `selenium_tests.login_test` all tests in all `unittest.TestCase` subclasses in the module.

## Hints / Links

Great overview of the Selenium Python API: https://selenium-python.readthedocs.io/
Official API documentation: https://seleniumhq.github.io/selenium/docs/api/py/api.html
Consider to use PageObjects: https://selenium-python.readthedocs.io/page-objects.html

Wait for everything! If something is not waited for, the test will sometimes not work.
