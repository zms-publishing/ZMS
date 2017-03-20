# encoding: utf-8

import unittest
import os
import random
from contextlib import contextmanager
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class SeleniumTestCase(unittest.TestCase):
    DEFAULT_TIMEOUT = 10 # seconds
    
    @classmethod
    def setUpClass(cls):
        cls._annotate_test_methods_to_make_a_screenshot_if_they_fail()
    
    def setUp(self):
        self.driver = webdriver.Firefox()
        
        # this ensures all find_element* methods retry up to 10 seconds for the searched 
        # element to appear in the dom. Essential if testing AJAX stuff.
        self.driver.implicitly_wait(self.DEFAULT_TIMEOUT)
        
        # self.addCleanup(self.driver.close) # doesn't work on mac?
        self.addCleanup(self.driver.quit)
    
    ## Generic helpers
    
    def _login(self):
        self.driver.get("http://localhost:8080/manage_main")
        
        # would be the propper way to login, but seems to not be supported by geckodriver yet
        # self.driver.switch_to.alert.authenticate('admin', 'admin')
        self.driver.switch_to.alert.send_keys('admin' + Keys.TAB + 'admin')
        self.driver.switch_to.alert.accept()
    
    def _wait(self, condition, timeout=DEFAULT_TIMEOUT):
        return WebDriverWait(self.driver, timeout).until(condition)
    
    def _wait_for_text(self, text, timeout=DEFAULT_TIMEOUT):
        return self._wait(EC.text_to_be_present_in_element((By.CSS_SELECTOR, 'body'), text), timeout=timeout)
    
    def _find_element(self, by, value, timeout=DEFAULT_TIMEOUT):
        self._wait(EC.presence_of_element_located((by, value)), timeout=timeout)
        return self.driver.find_element(by, value)
    
    # Modeled after http://www.obeythetestinggoat.com/how-to-get-selenium-to-wait-for-page-load-after-a-click.html
    @contextmanager
    def _wait_for_page_load(self, timeout=DEFAULT_TIMEOUT):
        old_page = self.driver.find_element_by_tag_name('html')
        yield
        WebDriverWait(self.driver, timeout).until(
            EC.staleness_of(old_page)
        )
    
    def _unique_test_output_filename(self, file_name_suffix, file_type):
        assert None not in (file_name_suffix, file_type), 'need strings here'
        
        def generate_path(file_name_suffix, file_type):
            if file_name_suffix != '':
                file_name_suffix = '-' + file_name_suffix
            
            target_directory = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                'test_output')
            
            prefix = '.'.join((
                self.__class__.__module__,
                self.__class__.__name__, 
                self._testMethodName))
            return os.path.join(target_directory, prefix + file_name_suffix + '.' + file_type)
        
        target_filename = generate_path(file_name_suffix, file_type)
        counter = 0
        while os.path.exists(target_filename):
            target_filename = generate_path(file_name_suffix + str(counter), file_type)
            counter += 1
        return target_filename
    
    def _save_screenshot_of_current_page(self, optional_file_name_suffix=''):
        target_filename = self._unique_test_output_filename(optional_file_name_suffix, 'png')
        self.driver.get_screenshot_as_file(target_filename)
    
    @classmethod
    def _annotate_test_methods_to_make_a_screenshot_if_they_fail(cls):
        test_methods = { name: getattr(cls, name) for name in dir(cls) if name.startswith('test') }
        for name, method in test_methods.items():
            import functools
            functools.wraps(method)
            def wrapper(self, *args, **kwargs):
                try:
                    return method(self, *args, **kwargs)
                except:
                    self._save_screenshot_of_current_page()
                    raise
            setattr(cls, name, wrapper)
    
    def _create_or_navigate_to_zms(self):
        # expects to be logged in
        # ensure we're on the manage_main page
        self._wait_for_text('Control_Panel')
        
        if 'sites' not in self.driver.page_source:
            # create folder
            select = Select(self._find_element(By.CSS_SELECTOR, 'select[name=":action"]'))
            with self._wait_for_page_load():
                select.select_by_visible_text('Folder') # already navigates to next page
            
            self._find_element(By.NAME, 'id').send_keys('sites')
            with self._wait_for_page_load():
                self._find_element(By.CSS_SELECTOR, 'input[type="submit"][value="Add"]').click()
        
        with self._wait_for_page_load():
            self._find_element(By.LINK_TEXT, 'sites').click()
            
        # detail page has loaded
        if 'href="zms/manage_workspace"' not in self.driver.page_source:
            # create zms
            # if no link with zms is there
            Select(self._find_element(By.CSS_SELECTOR, 'select[name=":action"]')).select_by_visible_text('ZMS')
            with self._wait_for_page_load():
                self._find_element(By.NAME, 'submit').click()
        
            # zms add page has loaded
            self._wait_for_text('Add ZMS-Instance')
            folder_id = self._find_element(By.ID, 'folder_id')
            folder_id.clear()
            folder_id.send_keys('zms')
            with self._wait_for_page_load():
                self._find_element(By.CSS_SELECTOR, 'button[value="Add"]').click()
        else:
            with self._wait_for_page_load():
                self._find_element(By.PARTIAL_LINK_TEXT, 'zms').click()
            with self._wait_for_page_load():
                self._find_element(By.PARTIAL_LINK_TEXT, 'content').click()
        
        # zms content edit page has loaded
        self._wait_for_text('ZMS - Python-based contentmanagement system')
    

class LoginTest(SeleniumTestCase):
    
    def test_login(self):
        self._login()
        
        # only accessible if login worked
        self._wait(EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, 'Control_Panel')))
        self.driver.find_element_by_partial_link_text('Control_Panel').click()
        self._wait_for_text('ZServer.HTTPServer.zhttp_server')
        self.assertIn('ZServer.HTTPServer.zhttp_server', self.driver.page_source)

class ScreenshotDemonstrationTest(SeleniumTestCase):
    
    def test_the_importance_of_waiting(self):
        self._login()
        self._save_screenshot_of_current_page('before-wait')
        self._wait_for_text('Contents')
        self._save_screenshot_of_current_page('after-wait')
    

class ScreenshotAfterFailingTest(SeleniumTestCase):
    
    def test_that_demonstrates_that_failing_tests_take_screenshots(self):
        self._login()
        self._wait_for_text('Contents')
        self.fail('Intentionally failed test')

class EditPageExample(SeleniumTestCase):
    
    def test_edit_page(self):
        self._login()
        self._create_or_navigate_to_zms()
        
        # this string will be added to the page
        MARKER = "%s-%s" % (self.id(), random.randint(0, 100000))
        
        ## add textarea
        
        # ensure menu is visible
        
        def hide_zmi_actions():
            # remove stray 'Textabschnitt' elements that linger and could catch later clicks 
            # on buttons because they overlap them
            self.driver.execute_script("$('.zmi-item.ZMSTextarea .zmi-action').mouseleave()")
            
        # seems the popup is only initialized once it is shown
        self.driver.execute_script("$('.zmi-item.ZMSTextarea .zmi-action').mouseenter()")
        el = self._find_element(By.CSS_SELECTOR, '.zmi-item.ZMSTextarea .zmi-action')
        dropdown = el.find_element_by_css_selector('.dropdown-toggle')
        self._wait(lambda driver: dropdown.is_displayed() and dropdown.is_enabled())
        # Not sure why, but the popup only opens reliably when waiting a bit.
        import time; time.sleep(2)
        dropdown.click()
        
        hide_zmi_actions()
        
        create_paragraph = el.find_element_by_link_text('Textabschnitt')
        self._wait(lambda driver: create_paragraph.is_displayed())
        
        hide_zmi_actions()
        
        create_paragraph.click()
        
        # wait until ckeditor is loaded
        iframe = self.driver.find_element_by_css_selector('iframe.cke_wysiwyg_frame')
        self.driver.switch_to.frame(iframe)
        self.driver.find_element_by_css_selector('body').send_keys(MARKER)
        
        # click insert
        self.driver.switch_to.default_content()
        hide_zmi_actions()
        self._find_element(By.XPATH, '//button[text()="Einfügen"]').click()
        
        # wait until saved
        self.driver.find_element_by_css_selector('.alert-success')
        
        # open preview
        with self._wait_for_page_load():
            self.driver.find_element_by_link_text("Vorschau").click()
        frame = self.driver.find_element_by_name("partner")
        self.driver.switch_to.frame(frame)
        
        # ensure text is there
        self.driver.find_element_by_xpath('//p[text()="%s"]' % MARKER)

if __name__ == "__main__":
    unittest.main()
