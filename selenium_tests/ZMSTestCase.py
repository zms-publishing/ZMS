# encoding: utf-8

from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from SeleniumTestCase import SeleniumTestCase
import time

class ZMSTestCase(SeleniumTestCase):
    
    def _set_up(self):
        self._login()
        self._create_or_navigate_to_zms()
        self.driver.get(self.driver.current_url)

    def _tear_down(self):
        pass

    def _show_zmi_action(self, id):
        # open actions-dropdown-menu
        el = self._find_element(By.CSS_SELECTOR, '#'+id+' .zmi-action')
        self._wait_for_ajax("$ZMI.actionList.over($('#"+id+" .zmi-action'))")
        
        # dropdown-toggle
        item = el.find_element_by_css_selector('.dropdown-toggle')
        self._wait_for_click(item, By.CSS_SELECTOR, '#'+id+' .zmi-action .dropdown-menu')
        
        return el

    def _hide_zmi_actions(self):
        # remove stray action elements that linger and could catch later clicks 
        # on buttons because they overlap them
        self.driver.execute_script("$('.zmi-item .zmi-action').mouseleave()")

    def _show_zmi_nav_tab(self, text, timeout=SeleniumTestCase.DEFAULT_TIMEOUT):
        with self._wait_for_page_load(timeout=timeout):
            # element = self._find_element(By.CSS_SELECTOR, '.main-nav a'%text.lower(), timeout=timeout)
            element = self._find_element(By.XPATH, '//*[contains(@class,"nav-tabs")]//a[text()="%s"]' % text, timeout=timeout)
            element.click()
