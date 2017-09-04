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
   
      def test_conf(self):
        print '<MetaobjManagerTest.test_conf>'
        self._login()
        self._create_or_navigate_to_zms()
        self.driver.get(self.driver.current_url)
        
        # open config
        navbar = self._find_element(By.CSS_SELECTOR, '.navbar-main')
        navbar.find_element_by_css_selector('.dropdown-toggle').click()
        navbar = navbar.find_element_by_link_text('Content-Objekte')
        self._wait(lambda driver: navbar.is_displayed())
        with self._wait_for_page_load():
            navbar.click()
        
        # wait until opened
        self._find_element(By.CSS_SELECTOR, 'body.metas.config')
        
        # open insert dialog
        self._find_element(By.CSS_SELECTOR, '.btn[title="Einfügen..."]').click()
        dialog = self._find_element(By.CSS_SELECTOR, '#zmiModalinsertObj')
        self._wait(lambda driver: dialog.is_displayed())
        dialog.find_element(By.CSS_SELECTOR, 'input[name="_meta_id"]').send_keys('LgTest')
        dialog.find_element(By.CSS_SELECTOR, 'input[name="_meta_name"]').send_keys('Test')
        with self._wait_for_page_load():
            dialog.find_element(By.CSS_SELECTOR, '.btn[value="Einfügen"]').click()
        
        # wait until saved
        self._find_element(By.CSS_SELECTOR, '.alert-success')
        
        # reload page
        with self._wait_for_page_load():
            self._find_element(By.CSS_SELECTOR, '.nav.nav-tabs .active').click()
        
        # open delete dialog
        self._find_element(By.CSS_SELECTOR, 'input[name="ids:list"][value="LgTest"]').click()
        self._find_element(By.CSS_SELECTOR, '.btn[title="Löschen..."]').click()
        wait = WebDriverWait(self.driver, 5)
        wait.until(EC.alert_is_present())
        with self._wait_for_page_load():
            self.driver.switch_to_alert().accept()
        
        # wait until saved
        self._find_element(By.CSS_SELECTOR, '.alert-success')
        
        print '</MetaobjManagerTest.test_conf>'


# python -m unittest selenium_tests.metaobj_manager_test.MetadictManagerTest
class MetadictManagerTest(example_test.SeleniumTestCase):

      def test_conf(self):
        print '<MetadictManagerTest.test_conf>'
        self._login()
        self._create_or_navigate_to_zms()
        self.driver.get(self.driver.current_url)
        
        # open config
        navbar = self._find_element('.navbar-main')
        navbar.find_element_by_css_selector('.dropdown-toggle').click()
        navbar.find_element_by_link_text('Meta-Attribute').click()
        
        # wait until opened
        self._find_element(By.CSS_SELECTOR, 'body.metas.config')
        
        # open import dialog
        self._find_element(By.CSS_SELECTOR, '.btn.btn-default[title="Importieren..."]').click()
        dialog = self._find_element(By.CSS_SELECTOR, '.modal-dialog')
        self.driver.execute_script("$('select#init').mouseenter()")
        time.sleep(1)
        #dialog.find_element_by_css_selector('.btn.btn-primary[value="Importieren"]').click()
        
        time.sleep(1)
        print '</MetadictManagerTest.test_conf>'


if __name__ == "__main__":
    unittest.main()
