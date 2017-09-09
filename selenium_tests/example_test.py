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

# python -m unittest selenium_tests.example_test.EditPageExample
class EditPageExample(ZMSTestCase):
    
    def test_edit(self):
        print "<EditPageExample.test_edit>"
        self._set_up()
        
        # this string will be added to the page
        MARKER = "%s-%s" % (self.id(), random.randint(0, 100000))
        
        ## add textarea
        
        # ensure menu is visible
        
        # seems the popup is only initialized once it is shown
        self.driver.execute_script("$('.zmi-item.ZMSTextarea .zmi-action').mouseenter()")
        el = self._find_element(By.CSS_SELECTOR, '.zmi-item.ZMSTextarea .zmi-action')
        dropdown = el.find_element_by_css_selector('.dropdown-toggle')
        self._wait(lambda driver: dropdown.is_displayed() and dropdown.is_enabled())
        # Not sure why, but the popup only opens reliably when waiting a bit.
        import time; time.sleep(2)
        dropdown.click()
        
        self._hide_zmi_actions()
        
        create_paragraph = el.find_element_by_link_text('Textabschnitt')
        self._wait(lambda driver: create_paragraph.is_displayed())
        
        self._hide_zmi_actions()
        
        create_paragraph.click()
        
        # wait until ckeditor is loaded
        iframe = self._find_element(By.CSS_SELECTOR, 'iframe.cke_wysiwyg_frame')
        self.driver.switch_to.frame(iframe)
        self._find_element(By.CSS_SELECTOR, 'body').send_keys(MARKER)
        
        # click insert
        self.driver.switch_to.default_content()
        self._hide_zmi_actions()
        self._find_element(By.XPATH, '//button[text()="Einfügen"]').click()
        
        # wait until saved
        self._find_element(By.CSS_SELECTOR, '.alert-success')
        
        # open preview
        with self._wait_for_page_load(roottag='frameset'):
            # workaround for https://github.com/mozilla/geckodriver/issues/322
            # where the click sometimes is swallowed. Should be fixed in the comming weeks
            self._find_element(By.LINK_TEXT, "Vorschau").click()
            try:
              self._find_element(By.LINK_TEXT, "Vorschau").click()
            except:
              pass
        
        frame = self._find_element(By.NAME, "partner")
        self.driver.switch_to.frame(frame)
        
        # ensure text is there
        self._find_element(By.XPATH, '//p[text()="%s"]' % MARKER)
        
        self._tear_down()
        print "<EditPageExample.test_edit>"

if __name__ == "__main__":
    unittest.main()
