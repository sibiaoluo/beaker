#!/usr/bin/python

from bkr.inttest.server.selenium import SeleniumTestCase
from bkr.inttest import data_setup
import unittest, time, re, os
from turbogears.database import session

class Menu(SeleniumTestCase):

    
    def setUp(self):
        self.verificationErrors = []
        self.selenium = self.get_selenium()
        self.selenium.start()
        try:
            self.logout()
        except:pass

        with session.begin():
            data_setup.create_device(device_class="IDE")
        self.login()
       
    def test_menulist(self):
        sel = self.selenium
        sel.open("")
        sel.click("link=All")
        sel.wait_for_page_to_load('30000')
        sel.click("link=My Systems") 
        sel.wait_for_page_to_load('30000')
        sel.click("link=Available")
        sel.wait_for_page_to_load('30000')
        sel.click("link=Free")
        sel.wait_for_page_to_load('30000')
        sel.click("link=All")
        sel.wait_for_page_to_load("30000")
        sel.click("link=IDE")
        sel.wait_for_page_to_load('30000')
        sel.click("link=Family")
        sel.wait_for_page_to_load('30000')
        sel.click("link=New Job")
        sel.wait_for_page_to_load('30000')
        sel.click("link=Watchdog")
        sel.wait_for_page_to_load('30000')
        sel.click("//ul[@id='Activity']/li[1]/a")
        sel.wait_for_page_to_load('30000')
        sel.click("link=Systems")
        sel.wait_for_page_to_load('30000')
        sel.click("link=Distros")
        sel.wait_for_page_to_load('30000')
    
    def tearDown(self):
        self.selenium.stop()
        self.assertEqual([], self.verificationErrors)

if __name__ == "__main__":
    unittest.main()
