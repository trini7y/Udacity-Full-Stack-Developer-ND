#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
from email.policy import default
import os
import sys
from distutils.command.config import config
import json
import dateutil.parser
import babel
from flask import (
    abort, 
    jsonify, 
    render_template,
    request, 
    flash, 
    redirect, 
    url_for
  )
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from datetime import datetime
from models import ( 
    Venue, 
    Show, 
    Artist, 
    app, 
    moment, 
    db, 
    migrate
  )
from forms import ShowForm, ArtistForm, VenueForm

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#






# TODO: connect to a local postgresql database;

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
    try:
        try:
            recently_artists = db.session.query(Artist).order_by(
                Artist.id.desc()).limit(10).all()
        except:
            flash(f"Error fetching recently listed artists!")

        try:
            recently_venues = db.session.query(Venue).order_by(
                Venue.id.desc()).limit(10).all()
        except:
            flash(f"Error fetching recently listed venues!")

        artists = []
        venues = []

        for artist in recently_artists:
            artists.append({
              'id': artist.id,
              'name': artist.name
            })

        for venue in recently_venues:
            venues.append({
              'id' :venue.id,
              'name':venue.name
            })

        data = {
            "artists": artists,
            "venues": venues
        }
    except:
        flash(f"Sorry, could not fetch recently listed data!",
              category="error")
        abort(500)
    return render_template('pages/home.html', data=data)



#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  try:
      data = []
      venues = db.session.query(Venue.city, Venue.state).distinct().all()
      for sc in venues:
        state_city = Venue.query.filter_by(state=sc.state).filter_by(city=sc.city).all()
        subdata = []
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M')

        for venue in state_city:
          subdata.append({
            'id': venue.id,
            'name': venue.name,
            'num_upcoming_show': Show.query.filter(db.and_(Show.created_time > current_time, Show.venue_id == venue.id)).count()
          })
        data.append({
          'city': sc.city,
          'state': sc.state,
          'venues':subdata
        })
  except Exception as e:
      print(e)
  finally:
    return render_template('pages/venues.html', areas=data )
  
  
def get_search_result(search_word, schema):
  try:
    data = schema.query.filter(db.func.lower(schema.name).like(
      f'%{search_word.lower()}%')).order_by('name').all()
    return data
  except Exception as e:
     print(e)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  try:
    data = get_search_result(request.form['search_term'], Venue)
    vens = []
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M')
    for venue in data:
       vens.append({
        'id': venue.id,
        'name': venue.name,
        'num_upcoming_show': Show.query.filter(db.and_(Show.created_time > current_time, Show.venue_id == venue.id)).count()
       })
    response = {
       'count': len(data),
       'data': vens
    }
  except:
    flash('Sorry, something went wrong while searching. Please try again', category="error")
  
  finally:
    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

 

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  data = {}
  try:
    venue = Venue.query.filter(Venue.id == venue_id).first()

    current_time = datetime.now().strftime('%Y-%m-%d %H:%M')
    past_events = db.session.query(Show).join(Artist).filter(
        db.and_(Show.created_time < current_time, Show.venue_id == venue_id)).all()
    past_shows = []
    for artist in past_events:
        past_show = {
          'artist_id':artist.id,
          'artist_name': artist.name,
          'artist_image_link': artist.image_link,
          'start_time': str(Show.current_date)
        }
        past_shows.append( past_show )
    
    upcoming_events = db.session.query(Show).join(Artist).filter(
        db.and_(Show.created_time > current_time, Show.venue_id == venue_id)).all()
    upcoming_shows = []
    for artist in upcoming_events:
        upcoming_show = {
          'artist_id':artist.id,
          'artist_name': artist.name,
          'artist_image_link': artist.image_link,
          'start_time': str(Show.current_date)
        }
        upcoming_shows.append( upcoming_show )

    data = {
        'id': venue.id,
        'name': venue.name,
        'genres': venue.genres,
        'address': venue.address,
        'city': venue.city,
        'state': venue.state,
        'phone': venue.phone,
        'website': venue.website_link,
        'facebook_link':venue.facebook_link,
        'seeking_talent': venue.seeking_talent,
        'seeking_description': venue.seeking_desc,
        'image_link': venue.image_link,
        'past_shows':past_shows,
        'upcoming_shows':upcoming_shows,
        'past_shows_count': len(past_shows),
        'upcoming_shows_count':len(upcoming_shows)
    }
   
  except:
      flash('Sorry, there is no info regarding' + venue.id, category='info')
  
  finally:
      return render_template('pages/show_venue.html', venue=data)
#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  form = VenueForm(request.form)
  try:
    if form.validate():
      venue = Venue(name=request.form['name'],  
      city=request.form['city'], 
      state=request.form['state'], 
      address=request.form['address'], 
      phone=request.form['phone'], 
      genres=request.form.getlist('genres', type=str), 
      image_link=request.form['image_link'], 
      facebook_link=request.form['facebook_link'], 
      seeking_talent=request.form.get('seeking_talent', type=bool), 
      website_link=request.form['website_link'], 
      seeking_desc=request.form['seeking_description'])
      db.session.add(venue)
      db.session.commit()
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except:
      db.session.rollback()
      flash('An error occurred. Artist ' + request.form['name']  + ' could not be listed.')
  finally:
      db.session.close()
      return render_template('pages/home.html', form=form)
 

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  try:
    Venue.query.filter(Venue.id == venue_id).delete()
    db.session.commit()
    flash('Venue with id' + venue_id + 'was deleted succesfully')
  except:
    flash('Venue with id' + venue_id + 'could not be deleted', category='error')
    db.session.rollback()
    abort(500)
  finally:
    db.session.close()
    return jsonify({"homeUrl": '/'})

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  data = []
  artists = db.session.query(Artist.id, Artist.name).all()
  for artist in artists:
    data.append({
      'id':artist.id,
      'name': artist.name
    })
    
  return render_template('pages/artists.html', artists=data)



@app.route('/artists/search', methods=['POST'])
def search_artists():
  response = {}
  try:
    data = get_search_result(request.form['search_term'], Artist)
    artists = []
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M')
    for artist in data:
      artists.append({
        'id': artist.id,
        'name':artist.name,
        'num_upcoming_show': Show.query.filter(db.and_(Show.created_time > current_time, Show.artist_id == artist.id)).count()
      })
    response = {
      'count':len(data),
      'data':artists
    }
      
  except:
      flash('Sorry, something went wrong while searching. Please try again', category="error")
   
  finally:
      return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  data = {}
  try:
    artist = Artist.query.filter(Artist.id == artist_id).first()
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M')
    past_events = db.session.query(Show).join(Venue).filter(
        db.and_(Show.created_time < current_time, Show.artist_id == artist_id)).all()
    past_shows = []
    for venue in past_events:
        past_show = {
          'venue_id':venue.id,
          'venue_name': venue.name,
          'venue_image_link': venue.image_link,
          'start_time': str(Show.current_date)
        }
        past_shows.append( past_show )
    
    upcoming_events = db.session.query(Show).join(Venue).filter(
        db.and_(Show.created_time > current_time, Show.artist_id == artist_id)).all()
    upcoming_shows = []
    for venue in upcoming_events:
        upcoming_show = {
          'venue_id':venue.id,
          'venue_name': venue.name,
          'venue_image_link': venue.image_link,
          'start_time': str(Show.current_date)
        }
        upcoming_shows.append( upcoming_show )

    data = {
        'id': artist.id,
        'name': artist.name,
        'genres': artist.genres,
        'city': artist.city,
        'state': artist.state,
        'phone': artist.phone,
        'website': artist.website_link,
        'facebook_link':artist.facebook_link,
        'seeking_venue': artist.seeking_venue,
        'seeking_description': artist.seeking_desc,
        'image_link': artist.image_link,
        'past_shows':past_shows,
        'upcoming_shows':upcoming_shows,
        'past_shows_count': len(past_shows),
        'upcoming_shows_count':len(upcoming_shows)
    }
   
  except:
      flash('Sorry, there is no info regarding' + artist.id, category='info')
  
  finally:
      return render_template('pages/show_artist.html', artist=data)


#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    try:
        data = Artist.query.filter(Artist.id == artist_id).first()
        artist_form = ArtistForm(name=data.name, city=data.city, 
                            state=data.state, phone=data.phone,
                            image_link=data.image_link, 
                            genres=data.genres,
                            facebook_link=data.facebook_link,
                            website_link=data.website_link,
                            seeking_venue=data.seeking_venue, 
                            seeking_description=data.seeking_desc
        )
    except:
        flash(f"Sorry, unable to load up the Artist Edit form.", category="error")
        abort(500)
    finally:
        return render_template('forms/edit_artist.html', form=artist_form, artist=data) 
  

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  form = ArtistForm(request.form)

  if form.validate():
      try:
        data = Artist.query.filter(Artist.id == artist_id).first() 
        data.name = request.form['name']
        data.city = request.form['city']
        data.genres = request.form.getlist('genres', type=str)
        data.state = request.form['state']
        data.phone = request.form['phone']
        data.image_link = request.form['image_link']
        data.facebook_link = request.form['facebook_link']
        data.website_link = request.form['website_link']
        data.seeking_venue = request.form.get('seeking_venue', type=bool)
        data.seeking_desc = request.form['seeking_description']
        db.session.commit()
        flash('You have successfully updated your information')
      except:
        flash('Sorry, the artist could not be updated', category ='error')
        db.session.rollback()
      finally:
        db.session.close()
  return redirect(url_for('show_artist', artist_id=artist_id))
  
  

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  try:
    data = Venue.query.filter(Venue.id == venue_id).first()
    venue_form = VenueForm(name=data.name, city=data.city, 
                            state=data.state, 
                            address=data.address,
                            phone=data.phone,
                            image_link=data.image_link, 
                            genres=data.genres,
                            facebook_link=data.facebook_link,
                            website_link=data.website_link,
                            seeking_talent=data.seeking_talent, 
                            seeking_description=data.seeking_desc
        )
  except:
      flash(f"Sorry, unable to load up the Venue Edit form.", category="error")
      abort(500)
  finally:
      return render_template('forms/edit_venue.html', form=venue_form, venue=data) 

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  form = VenueForm(request.form)
  if form.validate():
      try:
        data = Venue.query.filter(Venue.id == venue_id).first() 
        data.name = request.form['name']
        data.city = request.form['city']
        data.genres = request.form.getlist('genres', type=str)
        data.address = request.form['address']
        data.state = request.form['state']
        data.phone = request.form['phone']
        data.image_link = request.form['image_link']
        data.facebook_link = request.form['facebook_link']
        data.website_link = request.form['website_link']
        data.seeking_venue = request.form.get('seeking_venue', type=bool)
        data.seeking_desc = request.form['seeking_description']
        db.session.commit()
        flash('You have successfully updated your information')
      except:
        flash('Sorry, the venue could not be updated', category ='error')
        db.session.rollback()
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
    form = ArtistForm(request.form)
    try:
      if form.validate():
        artist = Artist(name=request.form['name'],  
        city=request.form['city'], 
        state=request.form['state'], 
        phone=request.form['phone'], 
        genres=request.form.getlist('genres', type=str), 
        image_link=request.form['image_link'], 
        facebook_link=request.form['facebook_link'], 
        seeking_venue=request.form.get('seeking_venue', type=bool), 
        website_link=request.form['website_link'], 
        seeking_desc=request.form['seeking_description'])
        # on successful db insert, flash success
        db.session.add(artist)
        db.session.commit()
        flash('Artist ' + request.form['name'] + ' was successfully listed!')

    except:
      db.session.rollback()
      flash('An error occurred. Artist ' + request.form['name']  + ' could not be listed.')
    finally:
      db.session.close()
    return render_template('pages/home.html', form=form)


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  data = []
  try:
    shows = Show.query.all()
    for show in shows:
      data.append({
        'venue_id': show.venue_id,
        'venue_name': Venue.query.filter( Venue.id == show.venue_id).first().name,
        'artist_name':Artist.query.filter( Artist.id == show.artist_id).first().name,
        'artist_image_link':Artist.query.filter( Artist.id == show.artist_id).first().image_link,
        'start_time': str(show.created_time)
      } )
  except:
      flash(f'Error fetching shows data')
  finally:
      return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm() 
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  try:
        artistFound = True
        venueFound = True
        if Artist.query.filter(Artist.id == request.form['artist_id']).count() == 0:
            artistFound = False
            raise ValueError

        if Venue.query.filter(Venue.id == request.form['venue_id']).count() == 0:
            venueFound = False
            raise ValueError

        show = Show(artist_id=request.form['artist_id'],
                    venue_id=request.form['venue_id'], created_time=datetime.fromisoformat(str(request.form['start_time'])))
        db.session.add(show)
        db.session.commit()
        # on successful db insert, flash success
        flash('Show was successfully listed!')
  except ValueError as e:
        flash(
            f"""Show could not be listed{f" because the {'Artist' if not artistFound else 'Venue' if not venueFound else ''} ID provided does not exist in our database" if not artistFound or not venueFound else f', because {e}'}!""", category="error")
        db.session.rollback()
        abort(500)
  except Exception as e:
        flash(
            f"""Show could not be listed{f', because {e}'}!""", category="error")
        db.session.rollback()
        abort(500)
  finally:
        db.session.close()
  return redirect(url_for('index'))


@app.route('/shows/search', methods=['POST'])
def search_show():
    response = {}
    try:
        shows = []
        print(request.form['filter_by'], request.form['filter_by'])
        if request.form['filter_by'] == 'venue':
            shows = db.session.query(Show).join(Venue).filter(Show.venue_id == Venue.id).filter(db.func.lower(Venue.name).like(
                f"%{request.form['search_term'].lower()}%")).order_by('id').all()
        if request.form['filter_by'] == 'artist':
            shows = db.session.query(Show).join(Artist).filter(Show.artist_id == Artist.id).filter(db.func.lower(Artist.name).like(
                f"%{request.form['search_term'].lower()}%")).order_by('id').all()
        print(shows)
        data = []

        for show in shows:
            info = {
              'venue_id': show.venue_id,
              'venue_name': show.venue.name,
              'artist_id': show.artist_id,
              'artist_name': show.artist.name,
              'artist_image_link': show.artist.image_link,
              'start_time': str(show.start_time)
            }
            data.append(info)
            response = {
              'count' : len(shows),
              'data' : data
            }
    except:
        flash(
            f"Sorry, an error occurred while fetching search results.", category="error")
        db.session.close()
        abort(500)
    finally:
        return render_template('pages/search_show.html', results=response, search_term=request.form.get('search_term', ''))


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
# if __name__ == '__main__':
#     app.run()

# Or specify port manually:

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

