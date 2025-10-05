from flask_sqlalchemy import SQLAlchemy
from app import db  # import db from app.py to avoid circular import

class Product(db.Model):
    product_id = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(100), nullable=False)

class Location(db.Model):
    location_id = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(100), nullable=False)

class ProductMovement(db.Model):
    movement_id = db.Column(db.String(50), primary_key=True)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())
    product_id = db.Column(db.String(50), db.ForeignKey('product.product_id'), nullable=False)
    from_location = db.Column(db.String(50), db.ForeignKey('location.location_id'), nullable=True)
    to_location = db.Column(db.String(50), db.ForeignKey('location.location_id'), nullable=True)
    qty = db.Column(db.Integer, nullable=False)
