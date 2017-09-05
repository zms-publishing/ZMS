# encoding: utf-8

import unittest
import os
import random
import time
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import example_test

# python -m unittest selenium_tests.simple_test.EditDocTest
class EditDocTest(example_test.SeleniumTestCase):
   
      def test_edit_doc(self):
        print "<EditDocTest.test_edit_doc>"
       
        self._login()
        self._create_or_navigate_to_zms()
        self.driver.get(self.driver.current_url)
       
        # get id
        zmi_item = self._find_element(By.CSS_SELECTOR, '.zmi-item.ZMSTextarea:last-of-type')
        id = zmi_item.get_attribute("id")
       
        # open actions-dropdown-menu
        el = self._find_element(By.CSS_SELECTOR, '#'+id+' .zmi-action')
        self.driver.execute_script("$('#"+id+" .zmi-action').mouseenter()")
       
        # dropdown-toggle
        time.sleep(1)
        dd_toggle = el.find_element_by_css_selector('.dropdown-toggle')
        self._wait(lambda driver: dd_toggle.is_displayed() and dd_toggle.is_enabled())
        dd_toggle.click()
      
        # click create document
        time.sleep(1)
        create_doc = el.find_element_by_link_text('Dokument')
        self._wait(lambda driver: create_doc.is_displayed())
        create_doc.click()
       
        # insert frame
        time.sleep(1)
        MARKER = "%s-%s" % (self.id(), random.randint(0, 100000))
        dialog = self._find_element(By.CSS_SELECTOR, '#zmiIframeAddDialog')
        self._wait(lambda driver: dialog.is_displayed())
        dialog.find_element(By.CSS_SELECTOR, '.title').send_keys(MARKER)
        dialog.find_element(By.CSS_SELECTOR, '.titlealt').send_keys(MARKER)
        with self._wait_for_page_load():
            dialog.find_element(By.XPATH, '//button[text()="Einfügen"]').click()
       
        # wait until saved
        self._find_element(By.CSS_SELECTOR, '.alert-success')
       
        # open properties tab
        with self._wait_for_page_load():
            self._find_element(By.XPATH, '//ul/li/a[text()="Eigenschaften"]').click()
       
        # change properties
        MARKER = "%s-%s" % (self.id(), random.randint(0, 100000))
        self._find_element(By.CSS_SELECTOR, '#tabProperties .title').send_keys(MARKER)
        self._find_element(By.CSS_SELECTOR, '#tabProperties .titlealt').send_keys(MARKER)
        with self._wait_for_page_load():
            self._find_element(By.XPATH, '//button[text()="Speichern"]').click()
       
        # wait until saved
        self._find_element(By.CSS_SELECTOR, '.alert-success')
       
        # get id from url
        url = self.driver.current_url
        id = 'zmi_item_'+url.split('/')[-2]
        
        # click parent breadcrumb
        li = self._find_element(By.CSS_SELECTOR, '.breadcrumb li:first-of-type')
        with self._wait_for_page_load():
            li.click()
       
        # open actions-dropdown-menu
        el = self._find_element(By.CSS_SELECTOR, '#'+id+' .zmi-action')
        self.driver.execute_script("$('#"+id+" .zmi-action').mouseenter()")
       
        # dropdown-toggle
        dd_toggle = el.find_element_by_css_selector('.dropdown-toggle')
        self._wait(lambda driver: dd_toggle.is_displayed() and dd_toggle.is_enabled())
        time.sleep(1)
        dd_toggle.click()
       
        # click delete document
        delete_doc = el.find_element_by_css_selector('.icon-trash')
        self._wait(lambda driver: delete_doc.is_displayed())
        delete_doc.click()
        wait = WebDriverWait(self.driver, 5)
        wait.until(EC.alert_is_present())
        with self._wait_for_page_load():
            self.driver.switch_to_alert().accept()
       
        # wait until deleted
        self._find_element(By.CSS_SELECTOR, '.alert-success')
       
        print "</EditDocTest.test_edit_doc>"


if __name__ == "__main__":
    unittest.main()
