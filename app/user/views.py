#app/user/views.py
#Third party imports
from flask import abort, flash, redirect, render_template, url_for, request
from flask_login import current_user, login_required
import json
import requests
import os



#Standard library imports
try:
    from urllib.parse import urljoin
except ImportError:
    from urlparse import urljoin 
import urllib
import urlparse
import re

#Local imports
from . import user
from forms import QrSearchForm
from .. import db
from ..models import QRcode
from ..__init__ import db_session
#import create_qr_code
#from create_qr_code import create_qr
#import read_qr_code
#from read_qr_code import read_qr



def create_qr(content):
    """
    Function to create qr code from user given content

    Put url into database
    How to get url so i can call api and get img back?

    """
    
    #Base URL
    api_url_base = 'http://api.qrserver.com/v1/create-qr-code/?data='

    #URL Content
    api_url_content = content
    #api_url = urljoin(api_url_base, api_url_content)
    api_url ='{0}{1}'.format(api_url_base, api_url_content)
    response = requests.get(api_url)
    if response.status_code == 200:
        #return response.content
        return api_url
    else:
        print('[!] HTTP {0} calling [{1}]'.format(response.status_code, api_url))
        return None

def read_qr(id):
    """
    Function that reads QR code; Returns response in JSON format

    """

    #Base URL
    api_url_base = 'http://api.qrserver.com/v1/read-qr-code/?fileurl='

    #URL Content
    qrcode = QRcode.query.get_or_404(id)
    url_encode = qrcode.qrcontent
    url_encoded = urllib.quote_plus(url_encode)
    api_url = ' {0}{1}'.format(api_url_base, url_encoded)

    response = requests.get(api_url)

    if response.status_code == 200:
        return json.loads(response.content)
    else:
        print('[!] HTTP {0} calling [{1}]'.format(response.status_code, api_url))
        return None

def save_changes(qrcode, form, new=False):
    """
    Save changes to database
    
    """
    #Get data from form and assign it to the correct attributes 
    #of the SQLAlchemy table object
    qrcode.name = form.name.data
    qrcode.description = form.description.data
    qrcode.qrcontent = create_qr(form.qrcontent.data)

    if new:
        #Add qrcode to database
        db_session.add(qrcode)
   # else:
        #In case QrCode name already exists
        #flash('Error: QrCode already exists.')

    #commit the data to the database
    db_session.commit()


#QRcode Database Views

@user.route('/qrcodes', methods=['GET', 'POST'])
@login_required
def list_qrcodes():
    """
    List all qrcodes

    """
    

    qrcodes = QRcode.query.all()

    return render_template('user/qrcodes/qrcodes.html', qrcodes=qrcodes, title= "QrCode Database")


@user.route('/qrdatabase/read/<int:id>', methods=['GET', 'POST'])
@login_required
def read_qrcode(id):
    """
    Read a qrcode in the database 

    """

    results = []
    qry = db_session.query(QRcode).filter(QRcode.id==id)
    qrcode = qry.first()
    #decoded = QRcode(name=qrcode.name, description=qrcode.description, qrcontent=read_qr(qrcode.qrcontent))
    #results = decoded
    qrcode.qrcontent = read_qr(qrcode.qrcontent)
    results = qrcode

    if not results:
        flash('Content could not be read')
        return redirect(url_for('user.list_qrcodes'))
    return render_template('user/qrcodes/read.html', action="Read", results=results, title="QrCode Read")


@user.route('/qrdatabase/search', methods=['GET', 'POST'])
@login_required
def search_qrcode():
    """ 
    Search a qrcode in the database

    """
    search_qrcode = True
    """
    qrcode = QRcode.query.get_or_404(id)
    form = QrContentForm(obj=qrcode)
    #qrname = qrcode.name
    #qrdescription = qrcode.description
    #qrcontent = qrcode.qrcontent
    flash('Searching for <str:name> QrCode.')
    return redirect(url_for('admin.list_qrcodes'))

    return render_template('admin/qrcodes/qrcode.html', action="Search",
                           add_qrcode=add_qrcode,
                           qrcode=qrcode, form=form, title="QrCode Search")
    """
    search = QrSearchForm(request.form)
    if request.method == 'POST':
        return search_qrcode_results(search)
    #redirect to 
    #return redirect(url_for('admin.list_qrcodes'))
    
    return render_template('user/qrcodes/search.html', action="Search",
                           form=search, title="QrCode Search")

@user.route('/qrdatabase/results/', methods=['GET', 'POST'])
@login_required
def search_qrcode_results(search):

    
    search_qrcode_results = True

    results =[]
    search_string = search.data['search']

    if search_string:
        if search.data['select'] == 'Id':
            qry = db_session.query(QRcode).filter(QRcode.id.contains(search_string))
            results = qry.all()
        elif search.data['select'] == 'Name':
            qry = db_session.query(QRcode).filter(QRcode.name.contains(search_string))
            results = qry.all()
        else:
            qry = db_session.query(QRcode)
            results = qry.all()
    else:
        qry = db_session.query(QRcode)
        results = qry.all()

    
    if not results:
        flash('No results found!')
        return redirect(url_for('user.search_qrcode'))
    else:
        return render_template('user/qrcodes/results.html', action="Results",
                               results=results, title="QrCode Results")


