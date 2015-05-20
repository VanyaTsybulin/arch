__author__ = 'mandriy'
# -*- coding: utf-8 -*-

import unittest
import os.path
from test_utils import open_web_driver, PersonsLookerLifecycle
from selenium.webdriver import Firefox, Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import TimeoutException


class PersonsHunterMainFunctionality(unittest.TestCase):

    def wait_that_work_is_done(self, driver):
        try:
            WebDriverWait(driver, 10).until(
                ec.text_to_be_present_in_element((By.ID, "doneWorkPercentage"), '100%')
            )
        except TimeoutException:
            return False
        return True

    def main_functionality_test(self, web_driver):
        root = os.path.split(os.path.dirname(__file__))[0] + '/'
        data = [u'asfasf\n Шевченко Т. Г.', u'Шевченко А. Н.\n asfafa', u'Путин В. В.']
        with PersonsLookerLifecycle(data, root):
            with open_web_driver(web_driver) as driver:
                driver.get('http://localhost:8080')
                driver.find_element_by_id('participate').click()
                driver.find_element_by_id('task').click()
                body = driver.find_element_by_tag_name("body")
                body.send_keys(Keys.CONTROL + 't')
                driver.get('http://localhost:8080')
                driver.find_element_by_id('info').click()
                self.assertTrue(self.wait_that_work_is_done(driver), 'Waiting for results.')
                driver.find_element_by_id('home').click()
                driver.find_element_by_id('result').click()
                driver.get('http://localhost:8080/report-download')
                persons = driver.find_element_by_tag_name('persons').find_elements_by_tag_name('person')
                self.assertListEqual([u'Шевченко Т. Г.', u'Шевченко А. Н.', u'Путин В. В.'],
                                     [person.text for person in persons],
                                     'Persons hunter result.')

    def test_in_Chrome(self):
        self.main_functionality_test(Firefox)

    def test_in_Firefox(self):
        self.main_functionality_test(Chrome)


