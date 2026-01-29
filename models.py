from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Bus(db.Model):
    __tablename__ = 'bus'

    id = db.Column(db.Integer, primary_key=True)
    bus_name = db.Column(db.String(100), nullable=False)
    bus_type = db.Column(db.String(50), nullable=False)
    from_location = db.Column(db.String(100), nullable=False)
    to_location = db.Column(db.String(100), nullable=False)
    journey_date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    reach_time = db.Column(db.Time, nullable=False)
    booked_seats = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    seats = db.relationship('BusSeat', backref='bus', cascade="all, delete")


class BusSeat(db.Model):
    __tablename__ = 'bus_seat'

    id = db.Column(db.Integer, primary_key=True)
    bus_id = db.Column(db.Integer, db.ForeignKey('bus.id'), nullable=False)
    seat_type = db.Column(db.String(10), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())


class Video(db.Model):
    __tablename__ = 'video'

    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())


class GlobalSettings(db.Model):
    __tablename__ = 'global_settings'

    id = db.Column(db.Integer, primary_key=True)
    total_booked_tickets = db.Column(db.Integer, default=0)
    savings_per_ticket = db.Column(db.Integer, default=0)
