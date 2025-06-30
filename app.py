#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import logging
from logging import Formatter, FileHandler
import dateutil.parser
import babel

from flask import Flask, render_template, request, flash, redirect, url_for, jsonify
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import text
from forms import *

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
# Note to self. if I move models to a seperate module, use below line and comment line above
# db.init_app(app)
migrate = Migrate(app, db)

# DONETODO: connect to a local postgresql database
# Testing my DB-kamalFyyurNatwest connection
with app.app_context():
  try:
    with db.engine.connect() as conn:
      # checking the version number here
      result = conn.execute(text("SELECT version()"))
      version_str = " ".join(result.scalar().split()[:2])
      # confirming the database name to ensure I am on the right one
      dbname_result = conn.execute(text("SELECT current_database()"))
      dbname = dbname_result.scalar()

      print(f"\nYESSSSS! Database connection successful.\nPostgreSQL version: {version_str}\n The Database name: {dbname}\n")
  except Exception as e:
    print("Oops... Database connection failed:", e)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
  __tablename__ = 'Venue'

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String)
  city = db.Column(db.String(120))
  state = db.Column(db.String(120))
  address = db.Column(db.String(120))
  phone = db.Column(db.String(120))
  image_link = db.Column(db.String(500))
  facebook_link = db.Column(db.String(120))
  # DONETODO: implement any missing fields, as a database migration using Flask-Migrate
  website_link = db.Column(db.String)
  seeking_talent = db.Column(db.Boolean, default=False)
  seeking_description = db.Column(db.String)
  # NOTE: based on research next line should only work with PostgreSQL DB. Other DB should use simple .string
  genres = db.Column(db.ARRAY(db.String), nullable=False)
  # Relationships
  shows = db.relationship('Show', back_populates='venue', cascade='all, delete-orphan')

  def __repr__(self):
    return f'<Venue {self.id} {self.name}>'

class Artist(db.Model):
  __tablename__ = 'Artist'

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String)
  city = db.Column(db.String(120))
  state = db.Column(db.String(120))
  phone = db.Column(db.String(120))
  # genres = db.Column(db.String(120)) # duplication here
  image_link = db.Column(db.String(500))
  facebook_link = db.Column(db.String(120))
  # DONETODO: implement any missing fields, as a database migration using Flask-Migrate
  website_link = db.Column(db.String)
  seeking_venue = db.Column(db.Boolean, default=False)
  seeking_description = db.Column(db.String)
  # NOTE: based on research next line should only work with PostgreSQL DB. Other DB should use simple .string
  genres = db.Column(db.ARRAY(db.String), nullable=False)
  # Relationships
  shows = db.relationship('Show', back_populates='artist', cascade='all, delete-orphan')

  def __repr__(self):
    return f'<Artist {self.id} {self.name}>'

# DONETODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Show(db.Model):
  __tablename__ = 'Show'

  id = db.Column(db.Integer, primary_key=True)
  venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
  artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
  start_time = db.Column(db.DateTime, nullable=False)

  # Relationships with venue and artist from above
  venue = db.relationship('Venue', back_populates='shows')
  artist = db.relationship('Artist', back_populates='shows')

  def __repr__(self):
    return f'<Show {self.id} of the Venue {self.venue_id} the Artist {self.artist_id}>'

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
    format = "EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
    format = "EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')

#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # DONETODO: replace with real venues data.
  #       I think DONE also: num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  data = []
  # this is getting all unique city & state pairs
  locations = Venue.query.with_entities(Venue.city, Venue.state).distinct().all()
  for city, state in locations:
    # showing all the venues in this specific area
    venues_in_area = Venue.query.filter_by(city=city, state=state).all()
    venue_data = []
    for venue in venues_in_area:
      # Summing up number of upcoming shows
      num_upcoming_shows = Show.query.filter(
        Show.venue_id == venue.id,
        Show.start_time > datetime.utcnow()
      ).count()
      venue_data.append({
        "id": venue.id,
        "name": venue.name,
        "num_upcoming_shows": num_upcoming_shows
      })
    data.append({
      "city": city,
      "state": state,
      "venues": venue_data
    })
  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # DONETODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term = request.form.get('search_term', '')
  # note case insensitive search
  venues = Venue.query.filter(Venue.name.ilike(f'%{search_term}%')).all()
  data = []
  for venue in venues:
    num_upcoming_shows = Show.query.filter(
      Show.venue_id == venue.id,
      Show.start_time > datetime.utcnow()
    ).count()
    data.append({
      "id": venue.id,
      "name": venue.name,
      "num_upcoming_shows": num_upcoming_shows,
    })
  response = {
    "count": len(data),
    "data": data
  }
  return render_template('pages/search_venues.html', results=response, search_term=search_term)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  venue = Venue.query.get_or_404(venue_id)
  now = datetime.utcnow()

  past_shows = []
  upcoming_shows = []

  for show in venue.shows:
    show_info = {
      "artist_id": show.artist.id,
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time": show.start_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    }
    if show.start_time < now:
      past_shows.append(show_info)
    else:
      upcoming_shows.append(show_info)

  data = {
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website_link,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
  }
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # DONETODO: insert form data as a new Venue record in the db, instead
  # DONETODO: modify data to be the data object returned from db insertion

  form = VenueForm()
  # error = False

  if form.validate_on_submit():
    # duplicate check
    existing_venue = Venue.query.filter_by(name=form.name.data, address=form.address.data).first()
    if existing_venue:
      flash('Oops ... it looks like a venue with this name and address already exists. Try again with a different name or address.')
      return render_template('forms/new_venue.html', form=form)
    try:
      new_venue = Venue(
        name=form.name.data,
        city=form.city.data,
        state=form.state.data,
        address=form.address.data,
        phone=form.phone.data,
        image_link=form.image_link.data,
        facebook_link=form.facebook_link.data,
        website_link=form.website_link.data,
        seeking_talent=form.seeking_talent.data,
        seeking_description=form.seeking_description.data or '',  # Default to empty string if no data
        genres=form.genres.data
      )
      db.session.add(new_venue)
      db.session.commit()
      # on successful db insert, flash success
      flash('YES! The venue' + new_venue.name + ' was successfully listed :)')
      return render_template('pages/home.html')
    except Exception as e:
      db.session.rollback()
      # DONETODO: on unsuccessful db insert, flash an error instead.
      # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
      # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
      flash(f'Unfortuantly, an error occurred. Venue {form.name.data} could not be listed. Error message: {str(e)}')
      error = True
    finally:
      db.session.close()
  else:
    # Collect errors from form validation (for user feedback, optional)
    errors = ", ".join([f"{field}: {', '.join(errs)}" for field, errs in form.errors.items()])
    flash(f'ERROR: Form validation failed! Please correct errors and try again. {errors}')

  # If error or validation failed, show the form again with errors
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/<int:venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  error = False
  try:
    venue = Venue.query.get(venue_id)
    if not venue:
      return jsonify({'success': False, 'message': 'Venue not found!'}), 404
    db.session.delete(venue)  # This honors cascade
    db.session.commit()
  except Exception as e:
    error = True
    db.session.rollback()
    print("Error during deletion:", e)
  finally:
    db.session.close()

  if error:
    return jsonify({'success': False, 'message': 'Venue was not successfully deleted!'}), 500
  else:
    return jsonify({'success': True, 'message': 'Venue was successfully deleted!'}), 200

#  Artists
#  ----------------------------------------------------------------

@app.route('/artists')
def artists():
  artists = Artist.query.all()
  data = []
  for artist in artists:
    data.append({
      "id": artist.id,
      "name": artist.name
    })
  return render_template('pages/artists.html', artists=data)
  # # DONETODO: replace with real data returned from querying the database

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # DONETODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term = request.form.get('search_term', '')
  artists = Artist.query.filter(Artist.name.ilike(f'%{search_term}%')).all()
  data = []
  for artist in artists:
    num_upcoming_shows = Show.query.filter(
      Show.artist_id == artist.id,
      Show.start_time > datetime.utcnow()
    ).count()
    data.append({
      "id": artist.id,
      "name": artist.name,
      "num_upcoming_shows": num_upcoming_shows,
    })
  response = {
    "count": len(data),
    "data": data
  }
  return render_template('pages/search_artists.html', results=response, search_term=search_term)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  artist = Artist.query.get_or_404(artist_id)
  now = datetime.utcnow()

  past_shows = []
  upcoming_shows = []

  for show in artist.shows:
    show_info = {
      "venue_id": show.venue.id,
      "venue_name": show.venue.name,
      "venue_image_link": show.venue.image_link,
      "start_time": show.start_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    }
    if show.start_time < now:
      past_shows.append(show_info)
    else:
      upcoming_shows.append(show_info)

  data = {
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website_link,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows)
  }
  return render_template('pages/show_artist.html', artist=data)

  # # DONETODO: replace with real artist data from the artist table, using artist_id

#  Update
#  ----------------------------------------------------------------

@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get_or_404(artist_id)

  # the form get prepopulated below when editing
  form.name.data = artist.name
  form.city.data = artist.city
  form.state.data = artist.state
  form.phone.data = artist.phone
  form.website_link.data = artist.website_link
  form.facebook_link.data = artist.facebook_link
  form.seeking_venue.data = artist.seeking_venue
  form.seeking_description.data = artist.seeking_description
  form.image_link.data = artist.image_link
  form.genres.data = artist.genres

  return render_template('forms/edit_artist.html', form=form, artist=artist)
  # DONETODO: populate form with fields from artist with ID <artist_id>

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # DONETODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  form = ArtistForm()
  artist = Artist.query.get_or_404(artist_id)
  error = False

  if form.validate_on_submit():
    try:
      artist.name = form.name.data
      artist.city = form.city.data
      artist.state = form.state.data
      artist.phone = form.phone.data
      artist.website_link = form.website_link.data
      artist.facebook_link = form.facebook_link.data
      artist.seeking_venue = form.seeking_venue.data
      artist.seeking_description = form.seeking_description.data
      artist.image_link = form.image_link.data
      artist.genres = form.genres.data

      db.session.commit()
    except Exception as e:
      error = True
      db.session.rollback()
    finally:
      db.session.close()

    if error:
      flash(f'Unfortunatly, an error occurred here. Artist {form.name.data} could not be updated.')
      return redirect(url_for('edit_artist', artist_id=artist_id))
    else:
      flash('YES! Artist ' + artist.name + ' was successfully updated!')
      return redirect(url_for('show_artist', artist_id=artist_id))
  else:
    flash('ERROR: Form validation failed! Please correct errors and try again. ')
    return redirect(url_for('edit_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get_or_404(venue_id)

  # DONETODO: populate form with values from venue with ID <venue_id>
  form.name.data = venue.name
  form.city.data = venue.city
  form.state.data = venue.state
  form.address.data = venue.address
  form.phone.data = venue.phone
  form.website_link.data = venue.website_link
  form.facebook_link.data = venue.facebook_link
  form.seeking_talent.data = venue.seeking_talent
  form.seeking_description.data = venue.seeking_description
  form.image_link.data = venue.image_link
  form.genres.data = venue.genres

  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # DONETODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  form = VenueForm(request.form)
  error = False
  try:
    venue = Venue.query.get_or_404(venue_id)
    venue.name = form.name.data
    venue.city = form.city.data
    venue.state = form.state.data
    venue.address = form.address.data
    venue.phone = form.phone.data
    venue.website_link = form.website_link.data
    venue.facebook_link = form.facebook_link.data
    venue.seeking_talent = form.seeking_talent.data
    venue.seeking_description = form.seeking_description.data
    venue.image_link = form.image_link.data
    venue.genres = form.genres.data
    db.session.commit()
  except Exception as e:
    error = True
    db.session.rollback()
    flash(f'unfortunately, an error occurred. Venue could not be updated on this occasion. Error: {str(e)}')
  finally:
    db.session.close()
  if not error:
    flash('YES! Venue was successfully updated :)')
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # DONETODO: insert form data as a new Venue record in the db, instead
  # DONETODO: modify data to be the data object returned from db insertion

  form = ArtistForm()  # Use WTForm, not request.form
  # error = False

  if form.validate_on_submit():
    try:
      new_artist = Artist(
        name=form.name.data,
        city=form.city.data,
        state=form.state.data,
        phone=form.phone.data,
        image_link=form.image_link.data,
        facebook_link=form.facebook_link.data,
        website_link=form.website_link.data,
        seeking_venue=form.seeking_venue.data,
        seeking_description=form.seeking_description.data,
        genres=form.genres.data
      )
      db.session.add(new_artist)
      db.session.commit()
      # push success message when DB inserted
      flash('The Artist ' + new_artist.name + ' was successfully listed :)')
      return render_template('pages/home.html')
    except Exception as e:
      db.session.rollback()
      # DONETODO: on unsuccessful db insert, flash an error instead.
      # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
      flash(f'Unfortunately, an error occurred. Artist {form.name.data} could not be listed. Error note: {str(e)}')
      error = True
    finally:
      db.session.close()
  else:
    flash('Unfortunately, form validation failed! Please correct errors and try again :)')

  # validation failed or error -> show the form again with errors
  return render_template('forms/new_artist.html', form=form)

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  shows = Show.query.join(Venue).join(Artist).all()
  data = []
  for show in shows:
    data.append({
      "venue_id": show.venue_id,
      "venue_name": show.venue.name,
      "artist_id": show.artist_id,
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time": show.start_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    })
  return render_template('pages/shows.html', shows=data)
  # displays list of shows at /shows
  # # DONETODO: replace with real venues data.

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # DONETODO: insert form data as a new Show record in the db, instead

  form = ShowForm(request.form)
  error = False

  if form.validate_on_submit():
    try:
      new_show = Show(
        artist_id=form.artist_id.data,
        venue_id=form.venue_id.data,
        start_time=form.start_time.data
      )
      db.session.add(new_show)
      db.session.commit()
      # success message on DB insert
      flash('Yes! Show was successfully listed :) Lets party.')
      return render_template('pages/home.html')
    except Exception as e:
      db.session.rollback()
      # DONETODO: on unsuccessful db insert, flash an error instead.
      # e.g., flash('An error occurred. Show could not be listed.')
      # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
      flash(f'Unfortunaely, an error occurred. Show could not be listed. Error note: {str(e)}')
      error = True
    finally:
      db.session.close()
  else:
    error = True
    flash('Unfortunately, an error occurred. Show could not be listed due to invalid form data.')

  if error:
    return render_template('forms/new_show.html', form=form)

@app.errorhandler(404)
def not_found_error(error):
  return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
  return render_template('errors/500.html'), 500

if not app.debug:
  file_handler = FileHandler('error.log')
  file_handler.setFormatter(
    Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
  )
  app.logger.setLevel(logging.INFO)
  file_handler.setLevel(logging.INFO)
  app.logger.addHandler(file_handler)
  app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
  app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
