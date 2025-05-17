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
        user = User(username='tester', email='tester@example.com', role='admin', household_code=777)
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
            'role': 'admin',
            'password': 'adminpass',
            'confirm_password': 'adminpass'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Welcome, adminuser! Your account has been created', response.data)
    
    def test_register_user_with_valid_code(self):
        user = User.create_with_password(username='adminuser', email='admin@example.com', password='adminpass')
        db.session.add(user)
        db.session.commit()
                
        household = Household(code='7777', name='Admin Household', created_by=user.id)
        db.session.add(household)
        db.session.commit()


        user.household_id = household.id
        user.household_code = household.code 
        db.session.commit()

        response = self.client.post('/register', data={
            'username': 'user1',
            'email': 'user1@example.com',
            'role': 'user',
            'password': 'userpass',
            'confirm_password': 'userpass',
            'household_code': user.household_code
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Bill Analytics Page', response.data)

    def test_homepage_access(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
    
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_ctx.pop()