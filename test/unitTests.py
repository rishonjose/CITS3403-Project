import unittest
import datetime
from app import db, create_app
from app.models import User, BillEntry
from app.config import TestingConfig
from sqlalchemy.exc import IntegrityError

class UserTests(unittest.TestCase):
    def setUp(self):
        # Create app with TestingConfig
        app = create_app(TestingConfig)
        self.app_ctx = app.app_context()
        self.app_ctx.push()

        # Create all tables
        db.create_all()

    def test_register_user(self):
        user = User(username='test', email="test@test", profile_pic='default.png')
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

    def test_unique_username_and_email(self):
        user1 = User(username='unique', email='unique@test.com', profile_pic='default.png')
        user1.set_password('pass')
        db.session.add(user1)
        db.session.commit()

        user2 = User(username='unique', email='unique2@test.com', profile_pic='default.png')
        user2.set_password('pass')
        db.session.add(user2)
        with self.assertRaises(IntegrityError):
            db.session.commit()
        db.session.rollback()

        user3 = User(username='unique3', email='unique@test.com', profile_pic='default.png')
        user3.set_password('pass')
        db.session.add(user3)
        with self.assertRaises(IntegrityError):
            db.session.commit()
        db.session.rollback()

    def test_user_bill_entry_relationship(self):
        user = User(username='billuser', email='bill@test.com', profile_pic='default.png')
        user.set_password('pass')
        db.session.add(user)
        db.session.commit()

        entry = BillEntry(
            user_id=user.id,
            category='electricity',
            units=100.5,
            cost_per_unit=0.15,
            start_date=datetime.date(2024, 1, 1),
            end_date=datetime.date(2024, 1, 31)
        )
        db.session.add(entry)
        db.session.commit()

        self.assertEqual(user.entries.count(), 1)
        self.assertEqual(user.entries.first().category, 'electricity')
    
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_ctx.pop()