from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SelectMultipleField, DateTimeField, BooleanField
from wtforms.validators import DataRequired, URL, ValidationError
import re

# ENUM for clean coding
########################
class Genre:
    values = [
        'Alternative', 'Blues', 'Classical', 'Country', 'Electronic', 'Folk', 'Funk',
        'Hip-Hop', 'Heavy Metal', 'Instrumental', 'Jazz', 'Musical Theatre', 'Pop', 'Punk',
        'R&B', 'Reggae', 'Rock n Roll', 'Soul', 'Other'
    ]
    @classmethod
    def choices(cls):
        return [(v, v) for v in cls.values]

class State:
    values = [
        'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'DC', 'FL', 'GA', 'HI', 'ID', 'IL',
        'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MT', 'NE', 'NV', 'NH', 'NJ', 'NM', 'NY', 'NC',
        'ND', 'OH', 'OK', 'OR', 'MD', 'MA', 'MI', 'MN', 'MS', 'MO', 'PA', 'RI', 'SC', 'SD',
        'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY'
    ]
    @classmethod
    def choices(cls):
        return [(v, v) for v in cls.values]

# custom validators
########################
def genre_enum_validator(form, field):
    # DONETODO implement enum restriction
    for genre in field.data:
        if genre not in Genre.values:
            raise ValidationError(f"'{genre}' is not a valid genre.")

def state_enum_validator(form, field):
    # DONETODO implement validation logic for state
    if field.data not in State.values:
        raise ValidationError(f"'{field.data}' is not a valid US state abbreviation.")

def phone_validator(form, field):
    # DONETODO implement validation logic for state
    phone_pattern = r'^\d{3}-\d{3}-\d{4}$'
    if field.data and not re.match(phone_pattern, field.data):
        raise ValidationError('Invalid phone number. Format must be XXX-XXX-XXXX.')

def facebook_url_validator(form, field):
    if field.data and not field.data.startswith("https://www.facebook.com/"):
        raise ValidationError('Facebook link must start with "https://www.facebook.com/".')

# Forms
#########################
class ShowForm(FlaskForm):
    artist_id = StringField('artist_id')
    venue_id = StringField('venue_id')
    start_time = DateTimeField(
        'start_time',
        validators=[DataRequired()],
        default=datetime.today()
    )

class VenueForm(FlaskForm):
    name = StringField('name', validators=[DataRequired()])
    city = StringField('city', validators=[DataRequired()])
    state = SelectField(
        'state',
        validators=[DataRequired(), state_enum_validator],  # DONETODO: state enum validation
        choices=State.choices()
    )
    address = StringField('address', validators=[DataRequired()])
    phone = StringField(
        'phone',
        validators=[phone_validator]  # DONETODO: phone validation
    )
    image_link = StringField('image_link')
    genres = SelectMultipleField(
        'genres',
        validators=[DataRequired(), genre_enum_validator],  # DONETODO: genre enum validation
        choices=Genre.choices()
    )
    facebook_link = StringField(
        'facebook_link',
        validators=[URL(), facebook_url_validator]
    )
    website_link = StringField('website_link')
    seeking_talent = BooleanField('seeking_talent')
    seeking_description = StringField('seeking_description')

class ArtistForm(FlaskForm):
    name = StringField('name', validators=[DataRequired()])
    city = StringField('city', validators=[DataRequired()])
    state = SelectField(
        'state',
        validators=[DataRequired(), state_enum_validator],  # DONETODO: state enum validation
        choices=State.choices()
    )
    phone = StringField(
        'phone',
        validators=[phone_validator]  # DONETODO: phone validation
    )
    image_link = StringField('image_link')
    genres = SelectMultipleField(
        'genres',
        validators=[DataRequired(), genre_enum_validator],  # DONETODO: genre enum validation
        choices=Genre.choices()
    )
    facebook_link = StringField(
        'facebook_link',
        validators=[URL(), facebook_url_validator]
    )
    website_link = StringField('website_link')
    seeking_venue = BooleanField('seeking_venue')
    seeking_description = StringField('seeking_description')

