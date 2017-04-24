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
   
      def test_metaobj_conf(self):
       
        self._login()
        self._create_or_navigate_to_zms()
        self.driver.get(self.driver.current_url)
        
        # open config
        navbar = self._wait_for_element('.navbar-main')
        navbar.find_element_by_css_selector('.dropdown-toggle').click()
        navbar.find_element_by_link_text('Content-Objekte').click()
        
        # wait until opened
        self._find_element(By.CSS_SELECTOR, 'body.metas.config')
        
        # open import dialog
        self._find_element(By.CSS_SELECTOR, '.btn.btn-default[title="Importieren..."]').click()
        dialog = self._wait_for_element('iframe')
        self.driver.switch_to.frame(dialog)
        self.driver.execute_script("$('select#init').mouseenter()")
        time.sleep(2)
        dialog.find_element_by_css_selector('.btn.btn-primary[value="Importieren"]').click()
        
        time.sleep(5)
        print "Done"


      def test_metadict_conf(self):
       
        self._login()
        self._create_or_navigate_to_zms()
        self.driver.get(self.driver.current_url)
        
        # open config
        navbar = self._wait_for_element('.navbar-main')
        navbar.find_element_by_css_selector('.dropdown-toggle').click()
        navbar.find_element_by_link_text('Meta-Attribute').click()
        
        # wait until opened
        self._find_element(By.CSS_SELECTOR, 'body.metas.config')
        
        # open import dialog
        self._find_element(By.CSS_SELECTOR, '.btn.btn-default[title="Importieren..."]').click()
        dialog = self._wait_for_element('.modal-dialog')
        self.driver.execute_script("$('select#init').mouseenter()")
        time.sleep(2)
        dialog.find_element_by_css_selector('.btn.btn-primary[value="Importieren"]').click()
        
        time.sleep(5)
        print "Done"


if __name__ == "__main__":
    unittest.main()
