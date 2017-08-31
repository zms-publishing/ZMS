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

# python -m unittest selenium_tests.multilang_manager_test.MultilangManagerTest
class MultilangManagerTest(example_test.SeleniumTestCase):
   
      def test_conf(self):
        print '<MultilangManagerTest.test_conf>'
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
        self._find_element(By.CSS_SELECTOR, 'body.languages.config')
        
        # open insert dialog
        self._find_element(By.CSS_SELECTOR, '#changeLanguagesForm input[name="language_id"]').send_keys('eng')
        self._find_element(By.CSS_SELECTOR, '#changeLanguagesForm input[name="language_label"]').send_keys('English')
        with self._wait_for_page_load():
            self._find_element(By.CSS_SELECTOR, '#changeLanguagesForm .btn.btn-primary[value="Speichern"]').click()
        
        # wait until saved
        self._find_element(By.CSS_SELECTOR, '.alert-success')
        
        # open config
        navtabs = self._wait_for_element('.nav.nav-tabs')
        with self._wait_for_page_load():
            navtabs.find_element_by_link_text('Sprachen').click()
        
        # add key to lang-dict
        self._find_element(By.CSS_SELECTOR, '#changeLangDictForm input[name="_key"]').send_keys('QUALITY')
        self._find_element(By.CSS_SELECTOR, '#changeLangDictForm input[name="_value_ger"]').send_keys('Qualität')
        self._find_element(By.CSS_SELECTOR, '#changeLangDictForm input[name="_value_eng"]').send_keys('Quality')
        with self._wait_for_page_load():
            self._find_element(By.CSS_SELECTOR, '#changeLangDictForm .btn.btn-primary[value="Speichern"]').click()
        
        # wait until saved
        self._find_element(By.CSS_SELECTOR, '.alert-success')
        
        # open config
        navtabs = self._wait_for_element('.nav.nav-tabs')
        with self._wait_for_page_load():
            navtabs.find_element_by_link_text('Sprachen').click()
        
        # delete key from lang-dict
        self._find_element(By.CSS_SELECTOR, '#changeLangDictForm input[name="ids:list"][value="QUALITY"]').click()
        with self._wait_for_page_load():
            self._find_element(By.CSS_SELECTOR, '#changeLangDictForm .btn.btn-default[value="Löschen"]').click()
        
        # wait until saved
        self._find_element(By.CSS_SELECTOR, '.alert-success')
        
        # open config
        navtabs = self._wait_for_element('.nav.nav-tabs')
        with self._wait_for_page_load():
            navtabs.find_element_by_link_text('Sprachen').click()
        
        # delete language
        self._find_element(By.CSS_SELECTOR, '#changeLanguagesForm input[name="ids:list"][value="eng"]').click()
        with self._wait_for_page_load():
            self._find_element(By.CSS_SELECTOR, '#changeLanguagesForm .btn.btn-default[value="Löschen"]').click()
        
        # wait until saved
        self._find_element(By.CSS_SELECTOR, '.alert-success')
        
        print '</MultilangManagerTest.test_conf>'


if __name__ == "__main__":
    unittest.main()
