from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class BillEntry(db.Model):
    __tablename__ = 'bill_entries'

    id            = db.Column(db.Integer, primary_key=True)
    user_id       = db.Column(
                       db.Integer,
                       db.ForeignKey('users.id', ondelete='CASCADE'), 
                       nullable=False
                    )
    category      = db.Column(db.String(20), nullable=False) # e.g. 'Water', 'Electricity'
    units         = db.Column(db.Float,   nullable=False)    # numeric consumption
    cost_per_unit = db.Column(db.Float,   nullable=False)    # price per unit
    start_date    = db.Column(db.Date,    nullable=False)
    end_date      = db.Column(db.Date,    nullable=False)
    created_at    = db.Column(
                      db.DateTime,
                      server_default=db.func.now(),
                      nullable=False
                   )

    def __repr__(self):
        return (
            f"<BillEntry id={self.id!r} "
            f"category={self.category!r} "
            f"units={self.units!r} "
            f"cost_per_unit={self.cost_per_unit!r} "
            f"period={self.start_date}–{self.end_date}>"
        )
        
class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id            = db.Column(db.Integer, primary_key=True)
    username      = db.Column(db.String(80), unique=True, nullable=False)
    email         = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at    = db.Column(db.DateTime, server_default=db.func.now())
    entries       = db.relationship(
                       'BillEntry',
                       backref='user',
                       lazy='dynamic',
                       cascade='all, delete-orphan'
                    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
