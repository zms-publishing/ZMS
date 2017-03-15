import unittest
import os
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class SeleniumTestCase(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls._annotate_test_methods_to_make_a_screenshot_if_they_fail()
    
    def setUp(self):
        self.driver = webdriver.Firefox()
        
        # this ensures all find_element* methods retry up to 10 seconds for the searched 
        # element to appear in the dom. Essential if testing AJAX stuff.
        # self.driver.implicitly_wait(10)
        
        # self.addCleanup(self.driver.close) # doesn't work on mac?
        self.addCleanup(self.driver.quit)
    
    ## Generic helpers
    
    def _login(self):
        self.driver.get("http://localhost:8080/manage_main")
        
        # would be the propper way to login, but seems to not be supported by geckodriver yet
        # self.driver.switch_to.alert.authenticate('admin', 'admin')
        self.driver.switch_to.alert.send_keys('admin' + Keys.TAB + 'admin')
        self.driver.switch_to.alert.accept()
    
    def _wait(self, condition, timeout=10):
        return WebDriverWait(self.driver, 10).until(condition)
    
    def _wait_for_text(self, text, timeout=10):
        return self._wait(EC.text_to_be_present_in_element((By.CSS_SELECTOR, 'body'), text), timeout=timeout)
    
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

class LoginTest(SeleniumTestCase):
    
    def test_login(self):
        self._login()
        
        # only accessible if login worked
        self._wait(EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, 'Control_Panel')))
        self.driver.find_element_by_partial_link_text('Control_Panel').click()
        self._wait_for_text('ZServer.HTTPServer.zhttp_server')
        self.assertIn('ZServer.HTTPServer.zhttp_server', self.driver.page_source)

class ScreenshotDemonstrationTest(SeleniumTestCase):
    
    def test_smoke(self):
        self._login()
        self._save_screenshot_of_current_page('before-wait')
        self._wait_for_text('Contents')
        self._save_screenshot_of_current_page('after-wait')
    

class ScreenshotAfterFailingTest(SeleniumTestCase):
    
    def test_smoke(self):
        self._login()
        self._wait_for_text('Contents')
        self.fail('Intentionally failed test')
        

if __name__ == "__main__":
    unittest.main()
