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
        print '<test_metaobj_conf>'
        self._login()
        self._create_or_navigate_to_zms()
        self.driver.get(self.driver.current_url)
        
        # open config
        navbar = self._wait_for_element('.navbar-main')
        navbar.find_element_by_css_selector('.dropdown-toggle').click()
        navbar.find_element_by_link_text('Content-Objekte').click()
        
        # wait until opened
        self._find_element(By.CSS_SELECTOR, 'body.metas.config')
        
        # open insert dialog
        self._find_element(By.CSS_SELECTOR, '.btn.btn-primary[title="Einfügen..."]').click()
        dialog = self._wait_for_element('#zmiModalinsertObj')
        time.sleep(1)
        self._find_element(By.CSS_SELECTOR, '#zmiModalinsertObj input[name="_meta_id"]').send_keys('LgTest')
        self._find_element(By.CSS_SELECTOR, '#zmiModalinsertObj input[name="_meta_name"]').send_keys('Test')
        self._find_element(By.CSS_SELECTOR, '#zmiModalinsertObj .btn.btn-primary[value="Einfügen"]').click()
        
        # wait until saved
        self._find_element(By.CSS_SELECTOR, '.alert-success')
        
        # open config
        navtabs = self._wait_for_element('.nav.nav-tabs')
        navtabs.find_element_by_link_text('Content-Objekte').click()
        
        # open delete dialog
        self._find_element(By.CSS_SELECTOR, 'input[name="ids:list"][value="LgTest"]').click()
        self._find_element(By.CSS_SELECTOR, '.btn.btn-default[title="Löschen..."]').click()
        time.sleep(1)
        self.driver.switch_to_alert().accept()
        
        # wait until saved
        self._find_element(By.CSS_SELECTOR, '.alert-success')
        
        time.sleep(1)
        print '</test_metaobj_conf>'


      def test_metadict_conf(self):
        print '<test_metadict_conf>'
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
        time.sleep(1)
        #dialog.find_element_by_css_selector('.btn.btn-primary[value="Importieren"]').click()
        
        time.sleep(1)
        print '</test_metadict_conf>'


if __name__ == "__main__":
    unittest.main()
