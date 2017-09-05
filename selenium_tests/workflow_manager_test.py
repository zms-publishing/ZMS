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

# python -m unittest selenium_tests.workflow_manager_test.WorkflowManagerTest
class WorkflowManagerTest(example_test.SeleniumTestCase):
   
      def test_conf(self):
        print '<WorkflowManagerTest.test_conf>'
        self._login()
        self._create_or_navigate_to_zms()
        self.driver.get(self.driver.current_url)
        
        # open config
        navbar = self._find_element(By.CSS_SELECTOR, '.navbar-main')
        navbar.find_element_by_css_selector('.dropdown-toggle').click()
        navitem = navbar.find_element_by_link_text('System')
        self._wait(lambda driver: navitem.is_displayed())
        with self._wait_for_page_load():
            navitem.click()
        
        # wait until opened
        self._find_element(By.CSS_SELECTOR, 'body.customize.config')
        
        # insert workflow-manager
        select = Select(self._find_element(By.CSS_SELECTOR, '#Manager select#meta_type'))
        select.select_by_visible_text('ZMSWorkflowProvider')
        with self._wait_for_page_load():
            self._find_element(By.CSS_SELECTOR, '#Manager .btn[value="Add"]').click()
        
        # wait until saved
        self._find_element(By.CSS_SELECTOR, '.alert-success')
        
        # delete workflow-manager
        self._find_element(By.CSS_SELECTOR, '#Manager input[name="ids:list"][value="workflow_manager"]').click()
        with self._wait_for_page_load():
            self._find_element(By.CSS_SELECTOR, '#Manager .btn[value="Remove"]').click()
        
        # wait until saved
        self._find_element(By.CSS_SELECTOR, '.alert-success')
        
        print '</WorkflowManagerTest.test_conf>'


if __name__ == "__main__":
    unittest.main()
