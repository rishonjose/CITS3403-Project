from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, DateField, FloatField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, Optional, Length, ValidationError
from app.models import User
from flask_login import current_user

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[
        DataRequired(message="Email is required"),
        Email(message="Invalid email address")
    ])
    password = PasswordField('Password', validators=[
        DataRequired(message="Password is required")
    ])
    submit = SubmitField('Log In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(message="Username is required"),
        Length(min=2, max=20, message="Username must be between 2-20 characters")
    ])
    email = StringField('Email', validators=[
        DataRequired(message="Email is required"),
        Email(message="Invalid email address")
    ])
    password = PasswordField('Password', validators=[
        DataRequired(message="Password is required"),
        Length(min=8, message="Password must be at least 8 characters")
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(message="Please confirm your password"),
        EqualTo('password', message="Passwords must match")
    ])

    # ← New role field
    role = SelectField('Role', choices=[
        ('user',  'User'),
        ('admin', 'Admin')
    ], default='user', validators=[DataRequired()])
    
    household_code = StringField(
        'Household Code',
        validators=[
            Optional(),
            Length(min=0, max=16, message="Code must be at most 16 characters")
        ]
    )

    submit = SubmitField('Sign Up')
    
    def validate_household_code(self, field):
        # if they chose “member” they must supply a valid code
        if self.role.data == 'member':
            code = (field.data or "").strip().upper()
            if not code:
                raise ValidationError("Household code is required for members.")
            from app.models import Household
            if not Household.query.filter_by(code=code).first():
                raise ValidationError("That household code does not exist.")

    def validate_email(self, field):
        email = field.data.lower().strip()
        if User.query.filter_by(email=email).first():
            raise ValidationError('That email is already registered.')

    def validate_username(self, username_field):
        existing = User.query.filter_by(username=username_field.data.strip()).first()
        if existing:
            raise ValidationError("That username is already taken.")

class BillEntryForm(FlaskForm):
    category = SelectField('Category', choices=[
        ('Electricity', 'Electricity'),
        ('Water', 'Water'),
        ('Gas', 'Gas'),
        ('WiFi', 'WiFi'),
        ('Other', 'Other')
    ], validators=[DataRequired()])
    units = FloatField('Units', validators=[
        DataRequired(message="Please enter units used"),
    ])
    cost_per_unit = FloatField('Cost Per Unit', validators=[
        DataRequired(message="Please enter cost per unit"),
    ])
    start_date = DateField('Start Date', validators=[
        DataRequired(message="Please select a start date")
    ])
    end_date = DateField('End Date', validators=[
        DataRequired(message="Please select an end date")
    ])
    submit = SubmitField('Submit Bill')

class ProfileForm(FlaskForm):
    first_name = StringField('First Name', validators=[
        DataRequired(message="First name is required"),
        Length(min=1, max=20, message="First name must be between 1-20 characters")
    ])
    last_name = StringField('Last Name', validators=[
        Optional(),
        Length(max=20, message="Last name must be at most 20 characters")
    ])
    email = StringField('Email', validators=[
        DataRequired(message="Email is required"),
        Email(message="Invalid email address")
    ])
    password = PasswordField('New Password', validators=[
        Optional(),
        Length(min=8, message="Password must be at least 8 characters")
    ])
    submit = SubmitField('Save Changes')

    def validate_email(self, field):
        # only run when someone is actually logged in
        if not getattr(current_user, "is_authenticated", False):
            return

        new_email = field.data.lower().strip()
        if new_email != current_user.email:
            if User.query.filter_by(email=new_email).first():
                raise ValidationError('Email already in use.')

