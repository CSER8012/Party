from mongoengine import ValidationError
from wtforms import Form, StringField, PasswordField, validators, FloatField, DateTimeField
from wtforms.fields.html5 import EmailField
from wtforms.widgets import TextArea
from flask_wtf.file import FileField, FileAllowed
from flask_wtf import FlaskForm
from application import User

class RegistrationForm(FlaskForm):
    username = StringField('Your name',[validators.DataRequired(),validators.Length(min=2,max=20)])
    email = EmailField('Email Address',[validators.DataRequired(),validators.Email()])
    password = PasswordField('Set Password',[validators.DataRequired(),validators.EqualTo('confirm',message='Password must match!')])
    confirm = PasswordField('Confirm Password')

class LoginForm(FlaskForm):
    email = EmailField('Email Address', [validators.DataRequired(), validators.Email()])
    password = PasswordField('Password', [validators.DataRequired()])


class EditProfileForm(FlaskForm):
    username = StringField('Your name', [validators.DataRequired(), validators.Length(min=2, max=20)])
    bio = StringField('Bio',widget=TextArea(),validators=[validators.Length(max=200)])
    email = EmailField('Email Address', [validators.DataRequired(), validators.Email()])
    image = FileField('Profile image',
                      validators=[FileAllowed(['jpg', 'jpeg', 'png', 'gif'],
                                              'Only allow .jpg .png and .gif files')])

class PasswordForm(FlaskForm):
    old_password = PasswordField('Old Password', [validators.DataRequired()])
    new_password = PasswordField('New Password',[validators.DataRequired()])
    confirm = PasswordField('Confirm Password',[validators.DataRequired()])


class BasicPartyForm(FlaskForm):
    name = StringField('Party Name', validators=[validators.DataRequired(), validators.Length(min=3, max=30)])
    gplace = StringField('Google Place API')
    place = StringField('Place', validators=[validators.DataRequired()], widget=TextArea())
    lng = FloatField('Longitude', validators=[validators.Optional()])
    lat = FloatField('Latitude', validators=[validators.Optional()])
    start_datetime = DateTimeField('Start Time',
                                   validators=[validators.DataRequired()],
                                   format='%Y-%m-%d %H:%M')
    end_datetime = DateTimeField('End Time',
                                 validators=[validators.DataRequired()],
                                 format='%Y-%m-%d %H:%M')
    description = StringField('Description', widget=TextArea(), validators=[validators.Length(min=20)])


class EditPartyForm(BasicPartyForm):
    photo = FileField('Party photo',
                      validators=[FileAllowed(['jpg', 'jpeg', 'png', 'gif'],
                                              'Only allow .jpg .png and .gif files')])


class CancelPartyForm(FlaskForm):
    confirm = StringField('Are you sure you want to cancel this party? (say yes)',
                          validators=[validators.DataRequired()])

class exploreForm(FlaskForm):
    keyword = StringField("",validators = [validators.Optional()])




