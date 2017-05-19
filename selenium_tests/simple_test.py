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
       
        self._login()
        self._create_or_navigate_to_zms()
        self.driver.get(self.driver.current_url)
       
        # get id
        zmi_item = self._wait_for_element('.zmi-item.ZMSTextarea:last')
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
        self._find_element(By.CSS_SELECTOR, '#zmiIframeAddDialog .title').send_keys(MARKER)
        self._find_element(By.CSS_SELECTOR, '#zmiIframeAddDialog .titlealt').send_keys(MARKER)
       
        # click insert
        self._find_element(By.XPATH, '//button[text()="Einfügen"]').click()
       
        # wait until saved
        self._find_element(By.CSS_SELECTOR, '.alert-success')
       
        # open properties tab
        self._find_element(By.XPATH, '//ul/li/a[text()="Eigenschaften"]').click()
       
        # change properties
        MARKER = "%s-%s" % (self.id(), random.randint(0, 100000))
        self._find_element(By.CSS_SELECTOR, '#tabProperties .title').send_keys(MARKER)
        self._find_element(By.CSS_SELECTOR, '#tabProperties .titlealt').send_keys(MARKER)
       
        # click save
        self._find_element(By.XPATH, '//button[text()="Speichern"]').click()
       
        # wait until saved
        self._find_element(By.CSS_SELECTOR, '.alert-success')
       
        # get id from url
        url = self.driver.current_url
        id = 'zmi_item_'+url.split('/')[-2]
       
        # click parent breadcrumb
        li = self._wait_for_element('.breadcrumb li:first')
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
        time.sleep(1)
        delete_doc.click()
       
        # accept confirm
        time.sleep(1)
        self.driver.switch_to_alert().accept()
       
        # wait until deleted
        self._find_element(By.CSS_SELECTOR, '.alert-success')
       
        time.sleep(5)
        print "Done"


if __name__ == "__main__":
    unittest.main()