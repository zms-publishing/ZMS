import unittest
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class LoginTestCase(unittest.TestCase):

    def setUp(self):
        self.driver = webdriver.Firefox()
        
        # this ensures all find_element* methods retry up to 10 seconds for the searched 
        # element to appear in the dom. Essential if testing AJAX stuff.
        # self.driver.implicitly_wait(10)
        
        # self.addCleanup(self.driver.close) # doesn't work on mac?
        self.addCleanup(self.driver.quit)
    
    def _login(self):
        # would be the propper way to login, but seems to not be supported by geckodriver yet
        # self.driver.switch_to.alert.authenticate('admin', 'admin')
        self.driver.switch_to.alert.send_keys('admin' + Keys.TAB + 'admin')
        self.driver.switch_to.alert.accept()
    
    def _wait(self, condition, timeout=10):
        return WebDriverWait(self.driver, 10).until(condition)
    
    def _wait_for_text(self, text, timeout=10):
        return self._wait(EC.text_to_be_present_in_element((By.CSS_SELECTOR, 'body'), text), timeout=timeout)
    
    def test_login(self):
        self.driver.get("http://localhost:8080/manage_main")
        self._login()
        self._wait(EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, 'Control_Panel')))
        self.driver.find_element_by_partial_link_text('Control_Panel').click()
        self._wait_for_text('ZServer.HTTPServer.zhttp_server')
        self.assertIn('ZServer.HTTPServer.zhttp_server', self.driver.page_source)

if __name__ == "__main__":
    unittest.main()
