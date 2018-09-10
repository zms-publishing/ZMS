# encoding: utf-8

import unittest
import random
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from ZMSTestCase import ZMSTestCase

# python -m unittest selenium_tests.link_test.LinkTest
class LinkTest(ZMSTestCase):
   
      def test_edit(self):
        print "<LinkTest.test_edit>"
        self._set_up()
        
        # navigate tree to page
        self._find_element(By.XPATH, '//div[contains(text(), "Concept")]').click()
        self._find_element(By.XPATH, '//div[contains(text(), "Second Document")]').click()
        
        # open properties tab
        with self._wait_for_page_load():
            self._find_element(By.XPATH, '//ul/li/a[text()="Eigenschaften"]').click()
        
        # uid
        uid = self._find_element(By.CSS_SELECTOR, '.get_uid').text
        uid = '{$%s}'%uid[3:]
        
        # navigate home
        li = self._find_element(By.CSS_SELECTOR, '.breadcrumb li:first-of-type')
        with self._wait_for_page_load():
            li.click()
        
        # get id
        zmi_item = self._find_element(By.CSS_SELECTOR, '.zmi-item:last-of-type')
        id = zmi_item.get_attribute("id")
        
        # open actions-dropdown-menu and click create document
        el = self._show_zmi_action(id)
        item = el.find_element_by_link_text('Link')
        self._wait_for_click(item, By.CSS_SELECTOR, '#zmiIframeAddDialog')
        self._hide_zmi_actions()
        
        # insert frame
        MARKER = "%s-%s" % (self.id(), random.randint(0, 100000))
        dialog = self._find_element(By.CSS_SELECTOR, '#zmiIframeAddDialog')
        self._wait(lambda driver: dialog.is_displayed())
        dialog.find_element(By.CSS_SELECTOR, '.title').send_keys(MARKER)
        dialog.find_element(By.CSS_SELECTOR, '.titlealt').send_keys(MARKER)
        dialog.find_element(By.CSS_SELECTOR, '.attr_ref').send_keys(uid)
        with self._wait_for_page_load():
            dialog.find_element(By.XPATH, '//button[text()="Einfügen"]').click()
        
        # wait until saved
        self._find_element(By.CSS_SELECTOR, '.alert-success')
        
        # open properties tab
        with self._wait_for_page_load():
            self.driver.execute_script('window.scrollTo(0,0)')
            self._find_element(By.XPATH, '//ul/li/a[text()="Bearbeiten"]').click()
        
        # get id
        zmi_item = self._find_element(By.CSS_SELECTOR, '.zmi-item.ZMSLinkElement:first-of-type')
        id = zmi_item.get_attribute("id")
        
        # open actions-dropdown-menu and click delete document
        el = self._show_zmi_action(id)
        item = el.find_element_by_css_selector('.icon-trash')
        self._wait(lambda driver: item.is_displayed())
        with self._wait_for_page_load():
            item.click()
            self._wait(EC.alert_is_present())
            # wait = WebDriverWait(self.driver, 5)
            # wait.until(EC.alert_is_present())
            self.driver.switch_to.alert.accept()
       
        # wait until deleted
        self._find_element(By.CSS_SELECTOR, '.alert-success')
       
        self._tear_down()
        print "</LinkTest.test_edit>"


if __name__ == "__main__":
    unittest.main()
