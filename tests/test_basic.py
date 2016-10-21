import unittest
from flask import current_app
from app import create_app, db

class BasicsTestCase(unittest.TestCase):
    def setUp(self):
        """
        A sequence of operations needed to start basic tests.
        """
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        """
        A sequence of operations needed to end basic tests.
        """
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_app_exists(self):
        """
        Check if session exists.
        """
        self.assertFalse(current_app is None)

    def test_app_is_testing(self):
        """
        Check if app is launched using testing config.
        """
        self.assertTrue(current_app.config['TESTING'])
