import unittest
from app import db, create_app
from app.models import User
from app.config import TestingConfig

class SystemTestCase(unittest.TestCase):
    def setUp(self):
        # Create app with testing config
        self.app = create_app(TestingConfig)
        self.app_ctx = self.app.app_context()
        self.app_ctx.push()

        # Set up test client
        self.client = self.app.test_client()

        # Set up database
        db.create_all()

        # Add a test user
        user = User(username='tester', email='tester@example.com', profile_pic='default.png')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_ctx.pop()

    def test_homepage_access(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)