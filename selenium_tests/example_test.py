# encoding: utf-8

import unittest
import os
import random
from contextlib import contextmanager
from urlparse import urlparse, urljoin
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

class SeleniumTestCase(unittest.TestCase):
    DEFAULT_TIMEOUT = 10 # seconds
    
    @classmethod
    def setUpClass(cls):
        cls._annotate_test_methods_to_make_a_screenshot_if_they_fail()
        cls._read_credentials()
    
    def setUp(self):
        if self.ac_driver == 'Chrome':
            self.driver = webdriver.Chrome()
        else:
            profile = webdriver.FirefoxProfile();
            profile.set_preference("network.http.phishy-userpass-length", 255)
            self.driver = webdriver.Firefox(profile)
        
        # this ensures all find_element* methods retry up to 10 seconds for the searched 
        # element to appear in the dom. Essential if testing AJAX stuff.
        # This however requires a firefox newer than 45.8 (which is what we are stuck on the AC server right now)
        # self.driver.implicitly_wait(self.DEFAULT_TIMEOUT)
        # So until then, explicit waits have to be used.
        # @see http://selenium-python.readthedocs.io/waits.html#explicit-waits
        
        # self.addCleanup(self.driver.close) # doesn't work on mac?
        self.addCleanup(self.driver.quit)
    
    ## Low level test helpers
    
    def _wait(self, condition, timeout=DEFAULT_TIMEOUT):
        return WebDriverWait(self.driver, timeout).until(condition)
    
    def _wait_for_text(self, text, timeout=DEFAULT_TIMEOUT):
        return self._wait(EC.text_to_be_present_in_element((By.CSS_SELECTOR, 'body'), text), timeout=timeout)
    
    def _find_element(self, by, value, timeout=DEFAULT_TIMEOUT):
        print "_find_element",by,value
        self._wait(EC.presence_of_element_located((by, value)), timeout=timeout)
        return self.driver.find_element(by, value)
    
    def _wait_for_element(self, selector, timeout=DEFAULT_TIMEOUT):
      import time
      print "_wait_for_element",selector
      element = None
      start = time.time()
      while True:
        script = "return $('"+selector+"').get(0);"
        element = self.driver.execute_script(script)
        if time.time()-start > timeout or element is not None:
          break
        time.sleep(1)
      return element
    
    # Modeled after http://www.obeythetestinggoat.com/how-to-get-selenium-to-wait-for-page-load-after-a-click.html
    @contextmanager
    def _wait_for_page_load(self, timeout=DEFAULT_TIMEOUT):
        old_page = self.driver.find_element_by_tag_name('html')
        yield
        WebDriverWait(self.driver, timeout).until(
            EC.staleness_of(old_page)
        )
    
    def _reload_page(self):
        return self.driver.get(self.driver.current_url)
    
    ## High level test helpers
    
    def _login(self):
        # would be the propper way to login, but is not supported by geckodriver yet
        # self.driver.switch_to.alert.authenticate(self.login, self.password)
        # This stopped working with firefox 53
        # self.driver.switch_to.alert.send_keys(self.login + Keys.TAB + self.password)
        # self.driver.switch_to.alert.accept()
        
        # So we have to use the really old way (requires the network.http.phishy-userpass-length setting)
        login_url = urljoin(self.base_url, '/manage_main')
        parsed = urlparse(login_url)
        parsed = parsed._replace(netloc="%s:%s@%s" % (self.login, self.password, parsed.netloc))
        self.driver.get(parsed.geturl())
    
    def _create_or_navigate_to_zms(self):
        # expects to be logged in
        # ensure we're on the manage_main page
        self._wait_for_text('Control_Panel')
        
        if 0 == len(self.driver.find_elements(By.LINK_TEXT, 'sites')):
            # create folder
            select = Select(self._find_element(By.CSS_SELECTOR, 'select[name=":action"]'))
            try:
                with self._wait_for_page_load(timeout=5):
                    # doesn't trigger the page load if 'Folder' is already the choice made last time
                    select.select_by_visible_text('Folder')
            except TimeoutException:
                with self._wait_for_page_load():
                    self._find_element(By.NAME, 'submit').click()
            
            self._find_element(By.NAME, 'id').send_keys('sites')
            with self._wait_for_page_load():
                self._find_element(By.CSS_SELECTOR, 'input[type="submit"][value="Add"]').click()
        
        with self._wait_for_page_load():
            self._find_element(By.LINK_TEXT, 'sites').click()
        
        # detail page has loaded
        self._find_element(By.CSS_SELECTOR, 'input[value="Import/Export"]') # finished loading
        if 0 == len(self.driver.find_elements(By.PARTIAL_LINK_TEXT, 'zms (ZMS - Python-based contentmanagement')):
            # create zms
            # if no link with zms is there
            try:
                with self._wait_for_page_load(timeout=5):
                    # doesn't trigger the page load if 'ZMS' is already the choice made last time
                    Select(self._find_element(By.CSS_SELECTOR, 'select[name=":action"]')).select_by_visible_text('ZMS')
            except TimeoutException:
                with self._wait_for_page_load():
                    self._find_element(By.NAME, 'submit').click()
        
            # zms add page has loaded
            self._wait_for_text('Add ZMS-Instance')
            folder_id = self._find_element(By.ID, 'folder_id')
            folder_id.clear()
            folder_id.send_keys('zms')
            with self._wait_for_page_load(timeout=50): # this can take a while
                self._find_element(By.CSS_SELECTOR, 'button[value="Add"]').click()
        else:
            with self._wait_for_page_load():
                self._find_element(By.PARTIAL_LINK_TEXT, 'zms (ZMS - Python-based contentmanagement').click()
            with self._wait_for_page_load():
                self._find_element(By.PARTIAL_LINK_TEXT, 'content').click()
        
        # zms content edit page has loaded
        self._wait_for_text('ZMS - Python-based contentmanagement system')
    
    ## Plumbing
    
    def _unique_test_output_filename(self, file_name_suffix, file_type):
        assert None not in (file_name_suffix, file_type), 'need strings here'
        
        def generate_path(file_name_suffix, file_type):
            if file_name_suffix != '':
                file_name_suffix = '-' + file_name_suffix
            
            target_directory = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                'test_output')
            
            prefix = '.'.join((
                self.__class__.__module__,
                self.__class__.__name__, 
                self._testMethodName))
            return os.path.join(target_directory, prefix + file_name_suffix + '.' + file_type)
        
        target_filename = generate_path(file_name_suffix, file_type)
        counter = 0
        while os.path.exists(target_filename):
            target_filename = generate_path(file_name_suffix + str(counter), file_type)
            counter += 1
        return target_filename
    
    def _save_screenshot_of_current_page(self, optional_file_name_suffix=''):
        target_filename = self._unique_test_output_filename(optional_file_name_suffix, 'png')
        self.driver.get_screenshot_as_file(target_filename)
    
    @classmethod
    def _annotate_test_methods_to_make_a_screenshot_if_they_fail(cls):
        test_methods = { name: getattr(cls, name) for name in dir(cls) if name.startswith('test') }
        for name, method in test_methods.items():
            import functools
            functools.wraps(method)
            def wrapper(self, *args, **kwargs):
                try:
                    return method(self, *args, **kwargs)
                except:
                    self._save_screenshot_of_current_page()
                    raise
            setattr(cls, name, wrapper)
    
    @classmethod
    def _read_credentials(cls):
        here = os.path.dirname(os.path.abspath(__file__))
        credentials_path = os.path.join(here, 'credentials.txt')
        from ConfigParser import SafeConfigParser
        parser = SafeConfigParser()
        parser.read(credentials_path)
        parser.defaults()['driver'] = 'Firefox'
        cls.ac_driver = parser.get('ac_server', 'driver')
        cls.base_url = parser.get('ac_server', 'base_url')
        cls.login = parser.get('ac_server', 'login')
        cls.password = parser.get('ac_server', 'password')
    

class LoginTest(SeleniumTestCase):
    
    def test_login(self):
        self._login()
        
        # only accessible if login worked
        self._wait(EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, 'Control_Panel')))
        self.driver.find_element_by_partial_link_text('Control_Panel').click()
        self._wait_for_text('ZServer.HTTPServer.zhttp_server')
        self.assertIn('ZServer.HTTPServer.zhttp_server', self.driver.page_source)

class ScreenshotDemonstrationTest(SeleniumTestCase):
    
    def test_the_importance_of_waiting(self):
        # On fast systems, this test makes a screen shot before
        # the page is loaded (showing a white screen).
        # The take-away here is that you should always explicitly
        # declare what element you want to wait for before interacting
        # with it. Otherwise, tests will behave flakily, failing on
        # particularly fast or slow systems.
        self._login()
        self._save_screenshot_of_current_page('before-wait')
        self._wait_for_text('Contents')
        self._save_screenshot_of_current_page('after-wait')

"""
class ScreenshotAfterFailingTest(SeleniumTestCase):
    
    def test_that_demonstrates_that_failing_tests_take_screenshots(self):
        self._login()
        self._wait_for_text('Contents')
        self.fail('Intentionally failed test')
"""

# python -m unittest selenium_tests.example_test.EditPageExample
class EditPageExample(SeleniumTestCase):
    
    def test_edit_page(self):
        self._login()
        self._create_or_navigate_to_zms()
        
        # this string will be added to the page
        MARKER = "%s-%s" % (self.id(), random.randint(0, 100000))
        
        ## add textarea
        
        # ensure menu is visible
        
        def hide_zmi_actions():
            # remove stray 'Textabschnitt' elements that linger and could catch later clicks 
            # on buttons because they overlap them
            self.driver.execute_script("$('.zmi-item .zmi-action').mouseleave()")
        
        self.driver.get(self.driver.current_url)
        # seems the popup is only initialized once it is shown
        self.driver.execute_script("$('.zmi-item.ZMSTextarea .zmi-action').mouseenter()")
        el = self._find_element(By.CSS_SELECTOR, '.zmi-item.ZMSTextarea .zmi-action')
        dropdown = el.find_element_by_css_selector('.dropdown-toggle')
        self._wait(lambda driver: dropdown.is_displayed() and dropdown.is_enabled())
        # Not sure why, but the popup only opens reliably when waiting a bit.
        import time; time.sleep(2)
        dropdown.click()
        
        hide_zmi_actions()
        
        create_paragraph = el.find_element_by_link_text('Textabschnitt')
        self._wait(lambda driver: create_paragraph.is_displayed())
        
        hide_zmi_actions()
        
        create_paragraph.click()
        
        # wait until ckeditor is loaded
        iframe = self._find_element(By.CSS_SELECTOR, 'iframe.cke_wysiwyg_frame')
        self.driver.switch_to.frame(iframe)
        self._find_element(By.CSS_SELECTOR, 'body').send_keys(MARKER)
        
        # click insert
        self.driver.switch_to.default_content()
        hide_zmi_actions()
        self._find_element(By.XPATH, '//button[text()="Einfügen"]').click()
        
        # wait until saved
        self._find_element(By.CSS_SELECTOR, '.alert-success')
        
        # open preview
        with self._wait_for_page_load():
            # workaround for https://github.com/mozilla/geckodriver/issues/322
            # where the click sometimes is swallowed. Should be fixed in the comming weeks
            self._find_element(By.LINK_TEXT, "Vorschau").click()
            self._find_element(By.LINK_TEXT, "Vorschau").click()
        
        frame = self._find_element(By.NAME, "partner")
        self.driver.switch_to.frame(frame)
        
        # ensure text is there
        self._find_element(By.XPATH, '//p[text()="%s"]' % MARKER)


if __name__ == "__main__":
    unittest.main()
