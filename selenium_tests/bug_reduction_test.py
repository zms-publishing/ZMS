# encoding: utf-8

import unittest
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from ZMSTestCase import ZMSTestCase

# python -m unittest selenium_tests.bug_reduction_test.BugReductionTest
class BugReductionTest(ZMSTestCase):
    ###############################
    # You need to manually resize the browser window so the top toolbar _can_ be scrolled out of view.
    
    def _navigate_to_workflow(self):
        self._login()
        self._create_or_navigate_to_zms()
        # open config
        navbar = self._find_element(By.CSS_SELECTOR, '.navbar-main')
        navbar.find_element_by_css_selector('.dropdown-toggle').click()
        navitem = navbar.find_element_by_link_text('System')
        self._wait(lambda driver: navitem.is_displayed())
        with self._wait_for_page_load():
            navitem.click()
    
    def _insert_workflow(self):
        # insert workflow-manager
        select = Select(self._find_element(By.CSS_SELECTOR, '#Manager select#meta_type'))
        with self._wait_for_page_load():
            select.select_by_visible_text('ZMSWorkflowProvider')
        
        # wait until saved
        self._find_element(By.CSS_SELECTOR, '.alert-success')
    
    def _remove_workflow(self):
        # delete workflow-manager
        checkbox = self._find_element(By.CSS_SELECTOR, '#Manager input[name="ids:list"][value="workflow_manager"]')
        checkbox.send_keys(Keys.NULL)
        checkbox.click()
        with self._wait_for_page_load():
            self._find_element(By.CSS_SELECTOR, '#Manager .btn[value="Remove"]').click()
        
        # wait until saved
        self._find_element(By.CSS_SELECTOR, '.alert-success')
    
    def test_reproduction(self):
        missed_clicks = 0
        self._navigate_to_workflow()
        self._insert_workflow()
        for i in range(100):
            try:
                self._show_zmi_nav_tab('Workflow', timeout=4)
            except TimeoutException as ignored:
                print('missed'); missed_clicks += 1
                self._show_zmi_nav_tab('Workflow', timeout=2)
            self.driver.execute_script('window.scrollBy(0,350)')
            try:
                self._show_zmi_nav_tab('System', timeout=4)
            except TimeoutException as ignored:
                print('missed'); missed_clicks += 1
                self._show_zmi_nav_tab('System', timeout=2)
            self.driver.execute_script('window.scrollBy(0,350)')
        self._remove_workflow()
        self.assertEquals(missed_clicks, 0)

if __name__ == "__main__":
    unittest.main()
