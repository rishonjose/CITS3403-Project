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
        user = User(username='test',email="test@test")
        user.set_password('pass')
        db.session.add(user)
        db.session.commit()
        fetched_user = User.query.filter_by(username='test').first()
        self.assertIsNotNone(fetched_user)

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_ctx.pop()