#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from config import DATABASE_URL
from flask_migrate import Migrate
from models import db, Venue, Artist, Show
from sqlalchemy import func
from datetime import date
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#
app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)

# TODO: connect to a local postgresql database
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

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
  # TODO: replace with real venues data.
  try:
    result1 = Venue.query.add_columns(Venue.state, Venue.city).all()
    result2 = Venue.query.add_columns(Venue.id, Venue.name).all()
    result3 = Show.query.join(Venue, Venue.id==Show.venue_id ).filter(Show.start_time < date.today()).count()
    data=[]
    for i, _ in enumerate(result2):
      data.append(
        {
      "city": result1[i].city,
      "state": result1[i].state,
      "venues": [{
        "id": result2[i].id,
        "name": result2[i].name,
        "num_upcoming_shows": result3,
        }]
      }
      )
  except:
    print("in exception")
    flash('Oops! Something went wrong')
    return
  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  try:
    search_term = request.form.get('search_term')
    data = Venue.query.filter(Venue.name.ilike('%' + search_term + '%')).all()

    response={
      "count": len(data),
      "data": data
    }
  except:
    flash('Oops! Something went wrong')
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  try:
    result_venue = Venue.query.filter(Venue.id == venue_id).first()
    result_past_shows_count = Show.query.join(Venue, Venue.id==Show.venue_id ).filter(Show.start_time < date.today()).count()
    result_upcoming_shows_count = Show.query.join(Venue, Venue.id==Show.venue_id ).filter(Show.start_time > date.today()).count()
    
    result_past_shows = Show.query.join(Venue, Venue.id==Show.venue_id )\
      .join(Artist, Artist.id == Show.artist_id)\
      .add_columns(Artist.id.label('artist_id'), Artist.name.label('artist_name'), Artist.image_link.label('artist_image_link'), Show.start_time)\
      .filter(Show.start_time < date.today()).all()
    
    result_upcoming_shows = Show.query.join(Venue, Venue.id==Show.venue_id )\
      .join(Artist, Artist.id == Show.artist_id)\
      .add_columns(Artist.id.label('artist_id'), Artist.name.label('artist_name'), Artist.image_link.label('artist_image_link'), Show.start_time)\
      .filter(Show.start_time > date.today()).all()
    data={
      "id": result_venue.id,
      "name": result_venue.name,
      "genres": result_venue.genres,
      "address": result_venue.address,
      "city": result_venue.city,
      "state": result_venue.state,
      "phone": result_venue.phone,
      "website": result_venue.website,
      "facebook_link": result_venue.facebook_link,
      "seeking_talent": result_venue.seeking_talent,
      "seeking_description": result_venue.seeking_description,
      "image_link": result_venue.image_link,
      "past_shows": result_past_shows,
      "upcoming_shows": result_upcoming_shows,
      "past_shows_count": result_past_shows_count,
      "upcoming_shows_count": result_upcoming_shows_count,
    }
  except:
    flash('Oops! Something went wrong')
    return
  # data = list(filter(lambda d: d['id'] == venue_id, [data1, data2, data3]))[0]
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  try:
    name = request.form.get('name')
    city = request.form.get('city')
    state = request.form.get('state')
    genres = request.form.getlist('genres')
    
    address = request.form.get('address')
    phone = request.form.get('phone')
    image_link = request.form.get('image_link')
    facebook_link = request.form.get('facebook_link')
    website = request.form.get('website')
    seeking_talent = request.form.get('seeking_talent')
    seeking_description = request.form.get('seeking_description')
    
    # TODO: insert form data as a new Venue record in the db, instead
    data = Venue(
          name = name,
          city = city,
          state = state,
          genres = genres,
          address = address,
          phone = phone,
          image_link = image_link,
          facebook_link = facebook_link,
          website = website,
          seeking_talent = seeking_talent,
          seeking_description = seeking_description
    )
    # TODO: modify data to be the data object returned from db insertion
    db.session.add(data)
    db.session.commit()   
    # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except:
    db.session.rollback()
    # TODO: on unsuccessful db insert, flash an error instead.
    flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    return
  finally:
    db.session.close()
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  try:
    data = Artist.query.add_columns(Artist.id, Artist.name).all()
  except:
    flash('Oops! Something went wrong')
    return
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  try:
    search_term = request.form.get('search_term')
    data = Artist.query.filter(Artist.name.ilike('%' + search_term + '%')).all()

    response={
      "count": len(data),
      "data": data
    }
  except:
    flash('Oops! Something went wrong')
  finally:
    db.session.close()
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  try:
    result_artist = Artist.query.filter(Artist.id == artist_id).first()
    result_past_shows_count = Show.query.join(Artist, Artist.id==Show.artist_id ).filter(Show.start_time < date.today()).count()
    result_upcoming_shows_count = Show.query.join(Artist, Artist.id==Show.artist_id ).filter(Show.start_time > date.today()).count()
    
    result_past_shows = Show.query.join(Artist, Artist.id==Show.venue_id )\
      .join(Venue, Venue.id == Show.artist_id)\
      .add_columns(Venue.id.label('venue_id'), Venue.name.label('venue_name'), Venue.image_link.label('venue_image_link'), Show.start_time)\
      .filter(Show.start_time < date.today()).all()
    
    result_upcoming_shows  = Show.query.join(Artist, Artist.id==Show.venue_id )\
      .join(Venue, Venue.id == Show.artist_id)\
      .add_columns(Venue.id.label('venue_id'), Venue.name.label('venue_name'), Venue.image_link.label('venue_image_link'), Show.start_time)\
      .filter(Show.start_time > date.today()).all()

    data={
      "id": result_artist.id,
      "name": result_artist.name,
      "genres": result_artist.genres,
      "city": result_artist.city,
      "state": result_artist.state,
      "phone": result_artist.phone,
      "website": result_artist.website,
      "facebook_link": result_artist.facebook_link,
      "seeking_venue": result_artist.seeking_venue,
      "seeking_description": result_artist.seeking_description,
      "image_link": result_artist.image_link,
      "past_shows": result_past_shows,
      "upcoming_shows": result_upcoming_shows,
      "past_shows_count": result_past_shows_count,
      "upcoming_shows_count": result_upcoming_shows_count,
    }
  except:
    flash('Oops! Something went wrong')
    return
  finally:
    db.session.close()
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist={
    "id": 4,
    "name": "Guns N Petals",
    "genres": ["Rock n Roll"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "326-123-5000",
    "website": "https://www.gunsnpetalsband.com",
    "facebook_link": "https://www.facebook.com/GunsNPetals",
    "seeking_venue": True,
    "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
  }
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue={
    "id": 1,
    "name": "The Musical Hop",
    "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    "address": "1015 Folsom Street",
    "city": "San Francisco",
    "state": "CA",
    "phone": "123-123-1234",
    "website": "https://www.themusicalhop.com",
    "facebook_link": "https://www.facebook.com/TheMusicalHop",
    "seeking_talent": True,
    "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
  }
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  try:
    name = request.form.get('name')
    city = request.form.get('city')
    state = request.form.get('state')
    genres = request.form.getlist('genres')
    phone = request.form.get('phone')
    image_link = request.form.get('image_link')
    facebook_link = request.form.get('facebook_link')
    website = request.form.get('website')
    seeking_venue = request.form.get('seeking_venue')
    seeking_description = request.form.get('seeking_description')
    
    # TODO: insert form data as a new Venue record in the db, instead
    data = Artist(
          name = name,
          city = city,
          state = state,
          genres = genres,
          phone = phone,
          image_link = image_link,
          facebook_link = facebook_link,
          website = website,
          seeking_venue = seeking_venue,
          seeking_description = seeking_description
    )
    # TODO: modify data to be the data object returned from db insertion
    db.session.add(data)
    db.session.commit()   
    # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except:
    db.session.rollback()
    # TODO: on unsuccessful db insert, flash an error instead.
    flash('An error occurred. Artist ' + data.name + ' could not be listed.')
    return
  finally:
    db.session.close()
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  try:
    data =  Show.query.join(Venue, Venue.id==Show.venue_id)\
    .join(Artist, Artist.id==Show.artist_id)\
    .add_columns(Show.venue_id, Venue.name.label('venue_name')\
    , Show.artist_id, Artist.name.label('artist_name'), Artist.image_link, Show.start_time)
  except:
    flash('Oops! Something went wrong')
    return
  finally:
    db.session.close()
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  try:
    venue_id = request.form.get('venue_id')
    artist_id = request.form.get('artist_id')
    start_time = request.form.get('start_time')
  
    # TODO: insert form data as a new Venue record in the db, instead
    data = Show(
          venue_id = venue_id,
          artist_id = artist_id,
          start_time = start_time
    )
    # TODO: modify data to be the data object returned from db insertion
    db.session.add(data)
    db.session.commit()   
    # on successful db insert, flash success
    flash('Show was successfully listed!')
  except:
    db.session.rollback()
    # TODO: on unsuccessful db insert, flash an error instead.
    flash('An error occurred. Show could not be listed.')
  finally:
    db.session.close()
  return render_template('pages/home.html')

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
