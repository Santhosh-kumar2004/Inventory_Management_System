from flask import render_template, redirect, url_for
from app import app, db
from models import Product, Location, ProductMovement
from forms import ProductForm, LocationForm, ProductMovementForm

# Home
@app.route('/')
def home():
    return redirect(url_for('products'))

# Products
@app.route('/products', methods=['GET', 'POST'])
def products():
    form = ProductForm()
    if form.validate_on_submit():
        product = Product(product_id=form.product_id.data, name=form.name.data)
        db.session.add(product)
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

# Locations
@app.route('/locations', methods=['GET', 'POST'])
def locations():
    form = LocationForm()
    if form.validate_on_submit():
        location = Location(location_id=form.location_id.data, name=form.name.data)
        db.session.add(location)
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

# Movements
@app.route('/movements', methods=['GET', 'POST'])
def movements():
    form = ProductMovementForm()
    form.product.choices = [(p.product_id, p.name) for p in Product.query.all()]
    form.from_location.choices = [('', '---')] + [(l.location_id, l.name) for l in Location.query.all()]
    form.to_location.choices = [('', '---')] + [(l.location_id, l.name) for l in Location.query.all()]

    if form.validate_on_submit():
        movement = ProductMovement(
            movement_id=form.movement_id.data,
            timestamp=form.timestamp.data,
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

# Report
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
