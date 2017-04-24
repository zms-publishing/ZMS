# encoding: utf-8

import unittest
import time
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import example_test

# python -m unittest selenium_tests.metaobj_manager_test.MetaobjManagerTest
class MetaobjManagerTest(example_test.SeleniumTestCase):
   
      def test_import_conf(self):
       
        self._login()
        self._create_or_navigate_to_zms()
        self.driver.get(self.driver.current_url)
       
        # open config
        self._find_element(By.CSS_SELECTOR, 'a[title="Konfiguration"]').click()
        navbar = self._wait_for_element('.navbar-main')
        navbar_item = navbar.find_element_by_link_text('Content-Objekte')
        navbar_item.click()
       
        # wait until opened
        self._find_element(By.CSS_SELECTOR, 'body.metas.config')
       
        time.sleep(5)
        print "Done"


if __name__ == "__main__":
    unittest.main()
