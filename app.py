from flask import Flask, render_template, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, DateTimeField, SubmitField
from wtforms.validators import DataRequired
from datetime import datetime
import os
# ------------------ App Setup ------------------
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///inventory.db'
db = SQLAlchemy(app)

# ------------------ Models ------------------
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

# ------------------ Forms ------------------
class ProductForm(FlaskForm):
    product_id = StringField('Product ID', validators=[DataRequired()])
    name = StringField('Product Name', validators=[DataRequired()])
    submit = SubmitField('Save')

class LocationForm(FlaskForm):
    location_id = StringField('Location ID', validators=[DataRequired()])
    name = StringField('Location Name', validators=[DataRequired()])
    submit = SubmitField('Save')

class ProductMovementForm(FlaskForm):
    movement_id = StringField('Movement ID', validators=[DataRequired()])
    timestamp = DateTimeField('Timestamp (YYYY-MM-DD HH:MM:SS)', format='%Y-%m-%d %H:%M:%S', default=None)
    product = SelectField('Product', validators=[DataRequired()])
    from_location = SelectField('From Location')
    to_location = SelectField('To Location')
    qty = IntegerField('Quantity', validators=[DataRequired()])
    submit = SubmitField('Save')

# ------------------ Routes ------------------
@app.route('/')
def home():
    return redirect(url_for('products'))

# ----------- Products -----------
@app.route('/products', methods=['GET', 'POST'])
def products():
    form = ProductForm()
    if form.validate_on_submit():
        db.session.add(Product(product_id=form.product_id.data, name=form.name.data))
        db.session.commit()
        return redirect(url_for('products'))
    all_products = Product.query.all()
    return render_template('products.html', products=all_products, form=form)

@app.route('/products/edit/<string:product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)
    form = ProductForm(obj=product)
    if form.validate_on_submit():
        product.name = form.name.data
        db.session.commit()
        return redirect(url_for('products'))
    all_products = Product.query.all()
    return render_template('products.html', products=all_products, form=form)

@app.route('/products/delete/<string:product_id>', methods=['POST'])
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    # Delete related movements
    ProductMovement.query.filter_by(product_id=product_id).delete()
    db.session.delete(product)
    db.session.commit()
    return redirect(url_for('products'))

# ----------- Locations -----------
@app.route('/locations', methods=['GET', 'POST'])
def locations():
    form = LocationForm()
    if form.validate_on_submit():
        db.session.add(Location(location_id=form.location_id.data, name=form.name.data))
        db.session.commit()
        return redirect(url_for('locations'))
    all_locations = Location.query.all()
    return render_template('locations.html', locations=all_locations, form=form)

@app.route('/locations/edit/<string:location_id>', methods=['GET', 'POST'])
def edit_location(location_id):
    location = Location.query.get_or_404(location_id)
    form = LocationForm(obj=location)
    if form.validate_on_submit():
        location.name = form.name.data
        db.session.commit()
        return redirect(url_for('locations'))
    all_locations = Location.query.all()
    return render_template('locations.html', locations=all_locations, form=form)

@app.route('/locations/delete/<string:location_id>', methods=['POST'])
def delete_location(location_id):
    location = Location.query.get_or_404(location_id)
    # Delete related movements
    ProductMovement.query.filter(
        (ProductMovement.from_location==location_id) | 
        (ProductMovement.to_location==location_id)
    ).delete()
    db.session.delete(location)
    db.session.commit()
    return redirect(url_for('locations'))

# ----------- Movements -----------
@app.route('/movements', methods=['GET', 'POST'])
def movements():
    form = ProductMovementForm()
    # Populate dropdowns
    form.product.choices = [(p.product_id, p.name) for p in Product.query.all()]
    form.from_location.choices = [('', '---')] + [(l.location_id, l.name) for l in Location.query.all()]
    form.to_location.choices = [('', '---')] + [(l.location_id, l.name) for l in Location.query.all()]

    if form.validate_on_submit():
        movement = ProductMovement(
            movement_id=form.movement_id.data,
            timestamp=datetime.now(),  # automatically set current time
            product_id=form.product.data,
            from_location=form.from_location.data or None,
            to_location=form.to_location.data or None,
            qty=form.qty.data
        )
        db.session.add(movement)
        db.session.commit()
        return redirect(url_for('movements'))

    all_movements = ProductMovement.query.order_by(ProductMovement.timestamp.desc()).all()
    return render_template('movements.html', movements=all_movements, form=form)
# ----------- Report -----------
@app.route('/report')
def report():
    report_data = []
    products = Product.query.all()
    locations = Location.query.all()
    for product in products:
        for location in locations:
            in_qty = db.session.query(db.func.sum(ProductMovement.qty)).filter_by(product_id=product.product_id, to_location=location.location_id).scalar() or 0
            out_qty = db.session.query(db.func.sum(ProductMovement.qty)).filter_by(product_id=product.product_id, from_location=location.location_id).scalar() or 0
            balance = in_qty - out_qty
            if balance > 0:
                report_data.append({'product': product.name, 'location': location.name, 'qty': balance})
    return render_template('report.html', report=report_data)

# ------------------ Run ------------------
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0",port=port)
