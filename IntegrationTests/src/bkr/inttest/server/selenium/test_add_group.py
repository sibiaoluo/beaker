#!/usr/bin/python
from bkr.inttest.server.selenium import SeleniumTestCase
from bkr.inttest import data_setup
import unittest, time, re, os
from turbogears.database import session

class AddGroup(SeleniumTestCase):
    def setUp(self):
        self.verificationErrors = []
        self.selenium = self.get_selenium()
        self.selenium.start()
        self.group_name = 'd_group_d'
        self.group_display_name = 'd_group_d'
                        
    def test_add_group(self):
        sel = self.selenium
        sel.open("")
        self.login()
        sel.click("link=Groups")
        sel.wait_for_page_to_load("3000")
        sel.click("link=Add ( + )")
        sel.wait_for_page_to_load("3000")
        sel.type("Group_display_name", "%s" % self.group_display_name)
        sel.type("Group_group_name", "%s" % self.group_name)
        sel.click("//input[@value='Save']")
        sel.wait_for_page_to_load("3000")
        self.failUnless(sel.is_text_present("OK"))
        self.failUnless(sel.is_text_present("%s" % self.group_display_name))
                                                                            
    def tearDown(self):
        self.selenium.stop()
        self.assertEqual([], self.verificationErrors)

if __name__ == "__main__":
    unittest.main()
