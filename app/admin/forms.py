#app/admin/forms.py

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired

class QrContentForm(FlaskForm):
    """
    Form for admin to create a qrcode

    """
    name = StringField('Name', validators=[DataRequired()])
    description = StringField('Description', validators=[DataRequired()])
    qrcontent = StringField('Qr Content', validators=[DataRequired()])
    submit = SubmitField('Submit')

class QrSearchForm(FlaskForm):
    """
    Form for user/admin to search a qrcode

    """
    choices = [('Id', 'Id'),
             ('Name', 'Name')]
    select = SelectField('Search for qrcode: ', choices=choices)
    search = StringField('')
