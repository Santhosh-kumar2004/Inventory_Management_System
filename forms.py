from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, DateTimeField, SubmitField
from wtforms.validators import DataRequired

class ProductForm(FlaskForm):
    product_id = StringField('Product ID', validators=[DataRequired()])
    name = StringField('Name', validators=[DataRequired()])
    submit = SubmitField('Save')

class LocationForm(FlaskForm):
    location_id = StringField('Location ID', validators=[DataRequired()])
    name = StringField('Name', validators=[DataRequired()])
    submit = SubmitField('Save')

class ProductMovementForm(FlaskForm):
    movement_id = StringField('Movement ID', validators=[DataRequired()])
    product = SelectField('Product', validators=[DataRequired()])
    from_location = SelectField('From Location')
    to_location = SelectField('To Location')
    qty = IntegerField('Quantity', validators=[DataRequired()])
    submit = SubmitField('Save')
