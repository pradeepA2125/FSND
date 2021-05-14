#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
from datetime import datetime
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for,jsonify,abort
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler, error
from flask_wtf import Form
from sqlalchemy.sql.elements import CollectionAggregate
from forms import *
from flask_migrate import Migrate
import sys
from utils import fix_json_array
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app,db)

# TODO: OK | connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

# I inspected the forms to see which fields were missing.


# from create show form it can be seen that only id's are needed to be connected, 
# it's basically a many to many relationship from last few lessons
Shows = db.Table('Shows', db.Model.metadata,
    db.Column('Venue_id', db.Integer, db.ForeignKey('Venue.id')),
    db.Column('Artist_id', db.Integer, db.ForeignKey('Artist.id')),
    db.Column('start_time', db.DateTime))

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
    

    # TODO: OK | implement any missing fields, as a database migration using Flask-Migrate
    genres = db.Column(db.ARRAY(db.String()),nullable=False)  # for genres 
    talent_required = db.Column(db.Boolean, nullable=False, default=False) # Looking for Talent checkbox
    seeking_description = db.Column(db.String(300)) # Description box
    website_link = db.Column(db.String(120))
    artists = db.relationship('Artist', secondary=Shows,backref=db.backref('venues', lazy=True))

    def __repr__(self):
        return '<Venue Id:{} , Name: {}>'.format(self.id, self.name)

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String())) #db.Column(db.String(120)) ,,, # easier this way
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # TODO: OK | implement any missing fields, as a database migration using Flask-Migrate
    venue_required = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String(300)) # Description box
    website_link = db.Column(db.String(120))

    def __repr__(self):
        return '<Artist Id:{} , Name: {}>'.format(self.id, self.name)

# TODO: OK | Implement Show and Artist models, and complete all model relationships and properties, as a database migration.



#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
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
  # TODO: OK | replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  gb_city_states = db.session.query(Venue.city, Venue.state).group_by(Venue.city, Venue.state).all() # group by city and state to get unique combinations

  data = []
  for uq_city_state in gb_city_states:
    
    inner_data = {"city":uq_city_state[0],"state": uq_city_state[1]}
    
    venues = []
    venues_for_cs = Venue.query.filter(Venue.city == uq_city_state[0],Venue.state == uq_city_state[1]).all()
    for venue in venues_for_cs:
      venue_details = {}
      num_upcoming_shows = db.session.query(Shows).filter(Shows.c.Venue_id == venue.id, datetime.now() < Shows.c.start_time ).count()
      #print(venue.name,num_upcoming_shows)
      venue_details['id'] = venue.id
      venue_details['name'] = venue.name
      venue_details['num_upcoming_shows'] = num_upcoming_shows
      venues.append(venue_details)
    inner_data['venues'] = venues
    data.append(inner_data)

    #print(venues_for_cs)
  # data=[{
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "venues": [{
  #     "id": 1,
  #     "name": "The Musical Hop",
  #     "num_upcoming_shows": 0,
  #   }, {
  #     "id": 3,
  #     "name": "Park Square Live Music & Coffee",
  #     "num_upcoming_shows": 1,
  #   }]
  # }, {
  #   "city": "New York",
  #   "state": "NY",
  #   "venues": [{
  #     "id": 2,
  #     "name": "The Dueling Pianos Bar",
  #     "num_upcoming_shows": 0,
  #   }]
  # }]
  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: OK | implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term = request.form.get('search_term','')
  venues = Venue.query.filter(Venue.name.ilike("%{}%".format(search_term))).all()
  response = {"count":len(venues),
  "data":[{"id":venue.id,
           "name":venue.name,
           "num_upcoming_shows":db.session.query(Shows)
           .filter(Shows.c.Venue_id == venue.id, datetime.now() < Shows.c.start_time ).count()} for venue in venues]}

  # response={
  #   "count": 1,
  #   "data": [{
  #     "id": 2,
  #     "name": "The Dueling Pianos Bar",
  #     "num_upcoming_shows": 0,
  #   }]
  # }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  try:
    venue = Venue.query.get(venue_id)
    fix_json_array(venue,"genres")
    venue.__dict__["seeking_venue"] = venue.talent_required
    #venue.__dict__["genres"] = venue.genres
    data = venue.__dict__.copy()
    past_shows_rows = db.session.query(Shows).filter(Shows.c.Venue_id == venue.id, datetime.now() > Shows.c.start_time ).all()
    past_shows = []
    for past_show in past_shows_rows:
      show = dict(past_show).copy()
      show["artist_id"] = past_show.Artist_id
      show["artist_name"] = Artist.query.get(past_show.Artist_id).name
      show["venue_image_link"] = Artist.query.get(past_show.Artist_id).image_link
      show["start_time"] = str(past_show.start_time)
      past_shows.append(show)
    upcoming_shows_rows = db.session.query(Shows).filter(Shows.c.Venue_id == venue.id, datetime.now() < Shows.c.start_time ).all()
    upcoming_shows = []
    for upcoming_show in upcoming_shows_rows:
      show = dict(upcoming_show).copy()
      show["artist_id"] = upcoming_show.Artist_id
      show["artist_name"] = Artist.query.get(upcoming_show.Artist_id).name
      show["venue_image_link"] = Artist.query.get(upcoming_show.Artist_id).image_link
      show["start_time"] = str(upcoming_show.start_time)
      upcoming_shows.append(show)
    data["past_shows"] = past_shows
    data['upcoming_shows'] = upcoming_shows
    data["past_shows_count"]= len(past_shows)
    data["upcoming_shows_count"] = len(upcoming_shows)
    #print(artist.genres,type(artist.genres))
  except:
    print(sys.exc_info())
    return render_template('errors/404.html')
  
  # data1={
  #   "id": 1,
  #   "name": "The Musical Hop",
  #   "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
  #   "address": "1015 Folsom Street",
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "123-123-1234",
  #   "website": "https://www.themusicalhop.com",
  #   "facebook_link": "https://www.facebook.com/TheMusicalHop",
  #   "seeking_talent": True,
  #   "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
  #   "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
  #   "past_shows": [{
  #     "artist_id": 4,
  #     "artist_name": "Guns N Petals",
  #     "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #     "start_time": "2019-05-21T21:30:00.000Z"
  #   }],
  #   "upcoming_shows": [],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 0,
  # }
  # data2={
  #   "id": 2,
  #   "name": "The Dueling Pianos Bar",
  #   "genres": ["Classical", "R&B", "Hip-Hop"],
  #   "address": "335 Delancey Street",
  #   "city": "New York",
  #   "state": "NY",
  #   "phone": "914-003-1132",
  #   "website": "https://www.theduelingpianos.com",
  #   "facebook_link": "https://www.facebook.com/theduelingpianos",
  #   "seeking_talent": False,
  #   "image_link": "https://images.unsplash.com/photo-1497032205916-ac775f0649ae?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=750&q=80",
  #   "past_shows": [],
  #   "upcoming_shows": [],
  #   "past_shows_count": 0,
  #   "upcoming_shows_count": 0,
  # }
  # data3={
  #   "id": 5,
  #   "name": "Park Square Live Music & Coffee",
  #   "genres": ["Rock n Roll", "Jazz", "Classical", "Folk"],
  #   "address": "34 Whiskey Moore Ave",
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "415-000-1234",
  #   "website": "https://www.parksquarelivemusicandcoffee.com",
  #   "facebook_link": "https://www.facebook.com/ParkSquareLiveMusicAndCoffee",
  #   "seeking_talent": False,
  #   "image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #   "past_shows": [{
  #     "artist_id": 5,
  #     "artist_name": "Matt Quevedo",
  #     "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
  #     "start_time": "2019-06-15T23:00:00.000Z"
  #   }],
  #   "upcoming_shows": [{
  #     "artist_id": 6,
  #     "artist_name": "The Wild Sax Band",
  #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #     "start_time": "2035-04-01T20:00:00.000Z"
  #   }, {
  #     "artist_id": 6,
  #     "artist_name": "The Wild Sax Band",
  #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #     "start_time": "2035-04-08T20:00:00.000Z"
  #   }, {
  #     "artist_id": 6,
  #     "artist_name": "The Wild Sax Band",
  #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #     "start_time": "2035-04-15T20:00:00.000Z"
  #   }],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 1,
  # }
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
  # TODO: OK | insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  venue_form = VenueForm(request.form)
  try:
      # Create a new instance of Venue with data from VenueForm
    newVenue = Venue(
      name=venue_form.name.data,
      genres=venue_form.genres.data,
      address=venue_form.address.data,
      city=venue_form.city.data,
      state=venue_form.state.data,
      phone=venue_form.phone.data,
      facebook_link=venue_form.facebook_link.data,
      image_link=venue_form.image_link.data,
      talent_required=venue_form.seeking_talent.data,
      seeking_description=venue_form.seeking_description.data,
      website_link = venue_form.website_link.data
      
      )
    db.session.add(newVenue)
    db.session.commit()
    # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except: 
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.',error)
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()

  # TODO: OK | on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: OK | Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  try:
    venue = Venue.query.get(venue_id)
    print(venue.artists)
    #shows corresponding to venues will automatically deleted because of the relationship added, no need to delete again
    #for artist in venue.artists:
      #db.session.query(Shows).filter(Shows.c.Artist_id==artist.id,Shows.c.Venue_id==venue.id).delete()
    db.session.delete(venue)
    db.session.commit()
  except:
    db.session.rollback()
    print(sys.exc_info())

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return jsonify({"result":"Success"})

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: OK | replace with real data returned from querying the 
  data= []
  artists = Artist.query.all()
  for artist in artists:
    data.append({"id":artist.id,"name":artist.name})
  # data=[{
  #   "id": 4,
  #   "name": "Guns N Petals",
  # }, {
  #   "id": 5,
  #   "name": "Matt Quevedo",
  # }, {
  #   "id": 6,
  #   "name": "The Wild Sax Band",
  # }]
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: OK | implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term = request.form.get('search_term','')
  artists = Artist.query.filter(Artist.name.ilike("%{}%".format(search_term))).all()
  response = {"count":len(artists),
  "data":[{"id":artist.id,
           "name":artist.name,
           "num_upcoming_shows":db.session.query(Shows).filter(Shows.c.Artist_id == artist.id, datetime.now() < Shows.c.start_time ).count()} for artist in artists]}
  #print(response)
  # response={
  #   "count": 1,
  #   "data": [{
  #     "id": 4,
  #     "name": "Guns N Petals",
  #     "num_upcoming_shows": 0,
  #   }]
  # }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  try:
    artist = Artist.query.get(artist_id)
    if artist == None:
      return render_template('errors/404.html')
    fix_json_array(artist,"genres")
    artist.__dict__["seeking_venue"] = artist.venue_required
    artist.__dict__["genres"] = artist.genres
    data = artist.__dict__.copy()
    past_shows_rows = db.session.query(Shows).filter(Shows.c.Artist_id == artist.id, datetime.now() > Shows.c.start_time ).all()
    past_shows = []
    for past_show in past_shows_rows:
      show = dict(past_show).copy()
      show["venue_id"] = past_show.Venue_id
      show["venue_name"] = Venue.query.get(past_show.Venue_id).name
      show["venue_image_link"] = Venue.query.get(past_show.Venue_id).image_link
      show["start_time"] = str(past_show.start_time)
      past_shows.append(show)
    upcoming_shows_rows = db.session.query(Shows).filter(Shows.c.Artist_id == artist.id, datetime.now() < Shows.c.start_time ).all()
    upcoming_shows = []
    for upcoming_show in upcoming_shows_rows:
      show = dict(upcoming_show).copy()
      show["venue_id"] = upcoming_show.Venue_id
      show["venue_name"] = Venue.query.get(upcoming_show.Venue_id).name
      show["venue_image_link"] = Venue.query.get(upcoming_show.Venue_id).image_link
      show["start_time"] = str(upcoming_show.start_time)
      upcoming_shows.append(show)
    data["past_shows"] = past_shows
    data['upcoming_shows'] = upcoming_shows
    data["past_shows_count"]= len(past_shows)
    data["upcoming_shows_count"] = len(upcoming_shows)
    #print(artist.genres,type(artist.genres))
  except:
    print(sys.exc_info())
    return render_template('errors/404.html')
  

  # data1={
  #   "id": 1,
  #   "name": "Guns N Petals",
  #   "genres": ["Rock n Roll"],
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "326-123-5000",
  #   "website": "https://www.gunsnpetalsband.com",
  #   "facebook_link": "https://www.facebook.com/GunsNPetals",
  #   "seeking_venue": True,
  #   "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
  #   "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #   "past_shows": [{
  #     "venue_id": 1,
  #     "venue_name": "The Musical Hop",
  #     "venue_image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
  #     "start_time": "2019-05-21T21:30:00.000Z"
  #   }],
  #   "upcoming_shows": [],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 0,
  # }
  # data2={
  #   "id": 5,
  #   "name": "Matt Quevedo",
  #   "genres": ["Jazz"],
  #   "city": "New York",
  #   "state": "NY",
  #   "phone": "300-400-5000",
  #   "facebook_link": "https://www.facebook.com/mattquevedo923251523",
  #   "seeking_venue": False,
  #   "image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
  #   "past_shows": [{
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2019-06-15T23:00:00.000Z"
  #   }],
  #   "upcoming_shows": [],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 0,
  # }
  # data3={
  #   "id": 6,
  #   "name": "The Wild Sax Band",
  #   "genres": ["Jazz", "Classical"],
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "432-325-5432",
  #   "seeking_venue": False,
  #   "image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "past_shows": [],
  #   "upcoming_shows": [{
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2035-04-01T20:00:00.000Z"
  #   }, {
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2035-04-08T20:00:00.000Z"
  #   }, {
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2035-04-15T20:00:00.000Z"
  #   }],
  #   "past_shows_count": 0,
  #   "upcoming_shows_count": 3,
  # }
  #data = list(filter(lambda d: d['id'] == artist_id, [data1, data2, data3]))[0]
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  # artist={
  #   "id": 4,
  #   "name": "Guns N Petals",
  #   "genres": ["Rock n Roll"],
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "326-123-5000",
  #   "website": "https://www.gunsnpetalsband.com",
  #   "facebook_link": "https://www.facebook.com/GunsNPetals",
  #   "seeking_venue": True,
  #   "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
  #   "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
  # }
  # TODO: OK | populate form with fields from artist with ID <artist_id>
  try:
    artist = Artist.query.filter(Artist.id == artist_id).first()
    fix_json_array(artist,"genres")
  except:
    flash('Artist ID:' + str(artist_id) + ' is not in database!')
    return render_template('pages/home.html')
  artist_data = artist.__dict__
  artist_data['seeking_venue'] = artist.venue_required
  form = ArtistForm(data=artist.__dict__) 

  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: OK | take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  artist_form = ArtistForm(request.form)
  try:
    # Create a new instance of Artist with data from ArtistForm
    artist = Artist.query.get(artist_id)
    artist.name=artist_form.name.data
    artist.genres=artist_form.genres.data
    artist.city=artist_form.city.data
    artist.state=artist_form.state.data
    artist.phone=artist_form.phone.data
    artist.facebook_link=artist_form.facebook_link.data
    artist.image_link=artist_form.image_link.data
    artist.venue_required=artist_form.seeking_venue.data
    artist.seeking_description=artist_form.seeking_description.data
    artist.website_link = artist_form.website_link.data
    db.session.add(artist)
    db.session.commit()
    # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully updated!')
    print('genres',artist.genres)
  except: 
    # TODO: OK | on unsuccessful db insert, flash an error instead.
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be updated.','error')
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()


  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  # venue={
  #   "id": 1,
  #   "name": "The Musical Hop",
  #   "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
  #   "address": "1015 Folsom Street",
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "123-123-1234",
  #   "website": "https://www.theseeking_venuemusicalhop.com",
  #   "facebook_link": "https://www.facebook.com/TheMusicalHop",
  #   "seeking_talent": True,
  #   "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
  #   "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
  # }
  # TODO: OK | populate form with values from venue with ID <venue_id>
  try:
    venue = Venue.query.filter(Venue.id == venue_id).first()
    fix_json_array(venue,"genres")
  except:
    flash('Venue ID:' + venue_id + ' is not in database!')
    return render_template('pages/home.html')
  venue_data = venue.__dict__
  venue_data['seeking_talent'] = venue.talent_required
  form = VenueForm(data=venue.__dict__) 
    
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: OK | take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  venue_form = VenueForm(request.form)
  try:
      # Create a new instance of Venue with data from VenueForm
    venue = Venue.query.get(venue_id)
    seeking_talent = venue_form.seeking_talent.data==True
    venue.name=venue_form.name.data
    venue.genres=venue_form.genres.data
    venue.address=venue_form.address.data
    venue.city=venue_form.city.data
    venue.state=venue_form.state.data
    venue.phone=venue_form.phone.data
    venue.facebook_link=venue_form.facebook_link.data
    venue.image_link=venue_form.image_link.data
    venue.seeking_description=venue_form.seeking_description.data
    venue.website_link = venue_form.website_link.data
    venue.talent_required=seeking_talent
    #db.session.add(newVenue)
    db.session.commit()
    # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully edited!')
  except: 
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.','error')
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()

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
  # TODO: OK | insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  artist_form = ArtistForm(request.form)
  try:
    # Create a new instance of Artist with data from ArtistForm
    artist = Artist(
      name=artist_form.name.data,
      genres=artist_form.genres.data,
      city=artist_form.city.data,
      state=artist_form.state.data,
      phone=artist_form.phone.data,
      facebook_link=artist_form.facebook_link.data,
      image_link=artist_form.image_link.data,
      venue_required=artist_form.seeking_venue.data,
      seeking_description=artist_form.seeking_description.data,
      website_link = artist_form.website_link.data
    )
    db.session.add(artist)
    db.session.commit()
    # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except: 
    # TODO: OK | on unsuccessful db insert, flash an error instead.
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.','error')
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: OK | replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  data = []
  try:
    shows = db.session.query(Shows).all()
    for show in shows:
      data.append({"venue_id":show.Venue_id,
      "venue_name":Venue.query.get(show.Venue_id).name,
      "artist_id":show.Artist_id,
      "artist_name":Artist.query.get(show.Artist_id).name,
      "artist_image_link":Artist.query.get(show.Artist_id).image_link,
      "start_time":str(show.start_time)})
    #print(dict(shows[0]))
  except:
    print(sys.exc_info())
    return render_template('errors/404.html')
  # data=[{
  #   "venue_id": 1,
  #   "venue_name": "The Musical Hop",
  #   "artist_id": 4,
  #   "artist_name": "Guns N Petals",
  #   "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #   "start_time": "2019-05-21T21:30:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 5,
  #   "artist_name": "Matt Quevedo",
  #   "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
  #   "start_time": "2019-06-15T23:00:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 6,
  #   "artist_name": "The Wild Sax Band",
  #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "start_time": "2035-04-01T20:00:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 6,
  #   "artist_name": "The Wild Sax Band",
  #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "start_time": "2035-04-08T20:00:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 6,
  #   "artist_name": "The Wild Sax Band",
  #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "start_time": "2035-04-15T20:00:00.000Z"
  # }]
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: OK |  insert form data as a new Show record in the db, instead
  show_form = ShowForm(request.form)
  try:
    # Create a new instance of Show with data from ShowForm
    show = Shows.insert().values(
            Artist_id=show_form.artist_id.data,
            Venue_id=show_form.venue_id.data,
            start_time=show_form.start_time.data
        )
    db.session.execute(show) 
    db.session.commit()
    # on successful db insert, flash success
    flash('Show was successfully listed!')
  except : 
    # TODO OK: on unsuccessful db insert, flash an error instead.
    flash('An error occurred. Show could not be listed.','error')
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()

  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
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
