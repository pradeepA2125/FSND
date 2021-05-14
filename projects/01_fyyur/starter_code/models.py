from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()

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

