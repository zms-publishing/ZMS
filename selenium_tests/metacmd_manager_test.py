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

# python -m unittest selenium_tests.metacmd_manager_test.MetacmdManagerTest
class MetacmdManagerTest(example_test.SeleniumTestCase):
   
      def test_conf(self):
        print '<MetacmdManagerTest.test_conf>'
        self._login()
        self._create_or_navigate_to_zms()
        self.driver.get(self.driver.current_url)
        
        # open config
        navbar = self._find_element(By.CSS_SELECTOR, '.navbar-main')
        navbar.find_element_by_css_selector('.dropdown-toggle').click()
        content_objects = navbar.find_element_by_link_text('Aktionen')
        self._wait(lambda driver: content_objects.is_displayed())
        with self._wait_for_page_load():
            content_objects.click()
        
        # wait until opened
        self._find_element(By.CSS_SELECTOR, 'body.metas.config')
        
        # open insert dialog
        self._find_element(By.CSS_SELECTOR, '.btn.btn-primary[title="Einfügen..."]').click()
        
        dialog = self._find_element(By.CSS_SELECTOR, '#zmiModalinsertObj')
        self._find_element(By.CSS_SELECTOR, '#zmiModalinsertObj input[name="_id"]').send_keys('manage_LgTest')
        self._find_element(By.CSS_SELECTOR, '#zmiModalinsertObj input[name="_name"]').send_keys('Test')
        self._find_element(By.CSS_SELECTOR, '#zmiModalinsertObj input[name="_title"]').send_keys('Test')
        self._find_element(By.CSS_SELECTOR, '#zmiModalinsertObj .btn[value="Einfügen"]').click()
        
        # wait until saved
        self._find_element(By.CSS_SELECTOR, '.alert-success')
        
        # open config (also removes .alert-success)
        navtabs = self._find_element(By.CSS_SELECTOR, '.nav.nav-tabs')
        with self._wait_for_page_load(timeout=5):
            navtabs.find_element_by_link_text('Aktionen').click()
        
        # open delete dialog
        self._find_element(By.CSS_SELECTOR, 'input[name="ids:list"][value="manage_LgTest"]').click()
        self._find_element(By.CSS_SELECTOR, '.btn.btn-default[title="Löschen..."]').click()
        self.driver.switch_to_alert().accept()
        
        # wait until saved
        self._find_element(By.CSS_SELECTOR, '.alert-success')
        
        print '</MetacmdManagerTest.test_conf>'


if __name__ == "__main__":
    unittest.main()
