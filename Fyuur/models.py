#INSERT INTO "Artist"(name, city, state, phone, genres, image_link, website_link) VALUES('Mavins House', 'Lagos', 'Lagos', '08097005320', '{"rock", "pop"}', 'link', 'link');  
from flask import Flask
from flask_moment import Moment
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime 


app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)



#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Show(db.Model):
    __tablename__ = 'shows'
    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id', ondelete='CASCADE'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id', ondelete='CASCADE'), nullable=False)
    created_time = db.Column(db.DateTime(), nullable=False)
    venue = db.relationship('Venue', back_populates='artist_show', lazy=True, cascade='all, delete', passive_deletes=True)
    artist = db.relationship('Artist', back_populates='venue_show', lazy=True, cascade='all, delete', passive_deletes=True)
    

class Venue(db.Model):
    __tablename__ = 'Venue'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String )
    city = db.Column(db.String(150))
    state = db.Column(db.String(150))
    address = db.Column(db.String(150))
    phone = db.Column(db.String(150))
    genres = db.Column(db.ARRAY(db.String))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(500))
    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    seeking_talent = db.Column(db.Boolean)
    website_link = db.Column(db.String(500))
    seeking_desc = db.Column(db.String())
    artist_show = db.relationship("Show", back_populates='venue', lazy=True, cascade='all, delete')

    def __repr__(self):
        return f'<Todo {self.id} {self.name} {self.city}>'

class Artist(db.Model):
    __tablename__ = 'Artist'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(150))
    state = db.Column(db.String(150))
    phone = db.Column(db.String())
    genres = db.Column(db.ARRAY(db.String))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(500))
    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    seeking_venue = db.Column(db.Boolean)
    website_link = db.Column(db.String(120))
    seeking_desc = db.Column(db.String())
    venue_show = db.relationship("Show",  back_populates='artist', lazy=True, cascade='all, delete')

    def __repr__(self):
        return f'<Todo {self.id} {self.name} {self.city}>'
db.create_all()
