#app/models.py

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app import db, login_manager
#from app import create/read qr code

class User(UserMixin, db.Model):

    """ 
    Create an User Table 

    """

    #Ensures table will be name in plural and not in singular
    #as is the name of the model

    __tablename__ ='users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(60), index=True, unique=True)
    username = db.Column(db.String(60), index=True, unique=True)
    first_name = db.Column(db.String(60), index=True)
    last_name = db.Column(db.String(60), index=True)
    password_hash = db.Column(db.String(60), index=True)
    #qrcode_id = db.Column(db.Integer, db.ForeignKey('qrcodes.id'))
    #qrcodes = db.relationship('QRcode', foreign_keys=[qrcode_id])
    is_admin = db.Column(db.Boolean, default=False)

    @property
    def password(self):
        """ 
        Prevent password from being accessed 
        
        """
        raise AttributeError('Password is not a readable attribute.')

    @password.setter
    def password(self, password):
        """ 
        Set password to a hashed password

        """
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        """
        Check if hashed password matches actual password

        """
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User: {}>'.format(self.username)

#Set up user_loader
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class QRcode(db.Model):
    """
    Create QRcode table

    """
    ___tablename__= 'qrcodes'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), unique=True)
    description = db.Column(db.String(200))
    qrcontent = db.Column(db.String(200))
    #users = db.relationship('User', backref='qrcode', lazy='dynamic')

    def __repr__(self):
        return '<QRCode: {}>'.format(self.name)

