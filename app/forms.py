from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, FloatField, SubmitField, DateField
from wtforms.validators import DataRequired, Email, EqualTo, Length, NumberRange, Optional
from datetime import datetime

# form for user login
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

# form for user signup
class SignupForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    height = FloatField('Height (in cm)', validators=[DataRequired(), NumberRange(min=1)])
    submit = SubmitField('Sign Up')

# form to add a new record
class AddRecordForm(FlaskForm):
    date = DateField('Date', default=datetime.today, validators=[DataRequired()], format='%Y-%m-%d')
    body_weight = FloatField('Body Weight (kg)', validators=[DataRequired()])
    muscle_weight = FloatField('Muscle Weight (kg)', validators=[DataRequired()])
    fat_weight = FloatField('Fat Weight (%)', validators=[DataRequired()])
    submit = SubmitField('Add Record')

# form to edit an existing record
class EditRecordForm(FlaskForm):
    date = DateField('Date', validators=[DataRequired()], format='%Y-%m-%d')
    body_weight = FloatField('Body Weight (kg)', validators=[DataRequired()])
    muscle_weight = FloatField('Muscle Weight (kg)', validators=[DataRequired()])
    fat_weight = FloatField('Fat Weight (%)', validators=[DataRequired()])
    submit = SubmitField('Update Record')