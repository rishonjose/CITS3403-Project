import unittest
from app import db, create_app
from app.models import User
from app.config import TestingConfig
from app.models import Household


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
    
    def test_login(self):
        response = self.client.post('/login', data={
            'email': 'tester@example.com',
            'password': 'password123'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'success', response.data) 

    def test_register_user_as_admin(self):
        response = self.client.post('/register', data={
            'username': 'adminuser',
            'email': 'admin@example.com',
            'Role': 'admin',
            'password': 'adminpass',
            'confirm': 'adminpass'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Account created for adminuser!', response.data)
    
    def test_register_user_with_valid_code(self):
        # Create a household with a known code
        household = Household(code='TESTCODE1')
        db.session.add(household)
        db.session.commit()

        response = self.client.post('/register', data={
            'username': 'user1',
            'email': 'user1@example.com',
            'Role': 'user',
            'password': 'userpass',
            'confirm': 'userpass',
            'household_code': 'TESTCODE1'
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Account created for user1!', response.data)

    def test_homepage_access(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
    
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_ctx.pop()