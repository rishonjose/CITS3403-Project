import unittest
from app import application, db
from app.models import User
from app.config import TestingConfig

class SystemTestCase(unittest.TestCase):
    def setUp(self):
        application.config.from_object(TestingConfig)
        self.app = application.test_client()
        self.app_ctx = application.app_context()
        self.app_ctx.push()
        db.create_all()

        user = User(username='tester', email='tester@example.com', profile_pic='default.png')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()

    def test_homepage_access(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_ctx.pop()