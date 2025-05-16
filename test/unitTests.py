import unittest
from app import application, db
from app.models import User
from app.config import TestingConfig

class UserTests(unittest.TestCase):
    def setUp(self):
        application.config.from_object(TestingConfig)
        self.app_ctx = application.app_context()
        self.app_ctx.push()
        db.create_all()

    def test_register_user(self):
        user = User(username='test',email="test@test",profile_pic='default.png')
        user.set_password('pass')
        db.session.add(user)
        db.session.commit()
        fetched_user = User.query.filter_by(username='test').first()
        self.assertIsNotNone(fetched_user)
    
    def test_password_hashing(self):
        user = User(username='test2', email='test2@test.com')
        user.set_password('mypassword')
        self.assertTrue(user.check_password('mypassword'))
        self.assertFalse(user.check_password('wrongpassword'))

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_ctx.pop()