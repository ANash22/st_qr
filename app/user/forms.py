#app/user/forms.py

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired


class QrSearchForm(FlaskForm):
    """
    Form for user/admin to search a qrcode

    """
    choices = [('Id', 'Id'),
             ('Name', 'Name')]
    select = SelectField('Search for qrcode: ', choices=choices)
    search = StringField('')
