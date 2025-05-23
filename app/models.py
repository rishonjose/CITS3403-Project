import uuid
from typing import Optional
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer, Float, Date, DateTime, ForeignKey
from .extensions import db
from flask import url_for
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


class BillEntry(db.Model):
    __tablename__ = 'bill_entries'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    category: Mapped[str] = mapped_column(String(20), nullable=False)
    units: Mapped[float] = mapped_column(Float, nullable=False)
    cost_per_unit: Mapped[float] = mapped_column(Float, nullable=False)
    start_date: Mapped[Date] = mapped_column(Date, nullable=False)
    end_date: Mapped[Date] = mapped_column(Date, nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=db.func.now(), nullable=False)

    # relationships
    shared_reports = db.relationship('SharedReport', back_populates='bill', cascade='all, delete-orphan')
    
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
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(128), nullable=True)
    profile_pic: Mapped[Optional[str]] = mapped_column(String(256), nullable=True, server_default='images/default-avatar-icon.jpg')
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=db.func.now())
    role: Mapped[str] = mapped_column(String(20), nullable=False, server_default='user')
    household_code: Mapped[Optional[str]] = mapped_column(String(8), unique=False, nullable=True)
    household_id: Mapped[Optional[int]] = mapped_column(ForeignKey('households.id', ondelete='SET NULL'), nullable=True)
    
    # relationships
    entries = db.relationship('BillEntry', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    sent_reports = db.relationship('SharedReport', foreign_keys='SharedReport.shared_by', back_populates='shared_by_user', cascade='all, delete-orphan')
    received_reports = db.relationship('SharedReport', foreign_keys='SharedReport.shared_with', back_populates='shared_with_user', cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    @classmethod
    def create_or_get_from_google(cls, email, username):
        user = cls.query.filter_by(email=email).first()
        if not user:
            user = cls(email=email, username=username)
            db.session.add(user)
            db.session.commit()
        return user
    
    @property
    def profile_picture_url(self):
        return self.profile_pic or url_for('static', filename='default-profile.png')

    @staticmethod
    def get_by_email(email):
        return User.query.filter_by(email=email.lower()).first()
    
    @staticmethod
    def create_with_password(username, email, password):
        user = User(username=username, email=email.lower())
        user.set_password(password)
        return user
    
    def get_display_name(self):
        return self.username or self.email.split('@')[0]
    
class Household(db.Model):
    __tablename__ = 'households'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str]  = mapped_column(String(8), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    created_by: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=db.func.now())

class SharedReport(db.Model):
    __tablename__ = 'shared_reports'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    bill_id: Mapped[int] = mapped_column(ForeignKey('bill_entries.id'), nullable=False)
    shared_with: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)
    shared_by: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)
    shared_at: Mapped[DateTime] = mapped_column(DateTime, server_default=db.func.now())
    can_edit: Mapped[bool] = mapped_column(db.Boolean, default=False)
    share_group_id: Mapped[str] = mapped_column(String(36), nullable=False, default=lambda: uuid.uuid4().hex)
    
    # **relationships for easy access**
    bill = db.relationship('BillEntry', back_populates='shared_reports')
    shared_by_user = db.relationship('User', foreign_keys=[shared_by], back_populates='sent_reports')
    shared_with_user = db.relationship('User', foreign_keys=[shared_with], back_populates='received_reports')