"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase


class SimpleTest(TestCase):
    
    @classmethod
    def setUpClass(cls):
        super(SimpleTest, cls).setUpClass()
        
    @classmethod
    def tearDownClass(cls):
        super(SimpleTest, cls).tearDownClass()
    
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)
