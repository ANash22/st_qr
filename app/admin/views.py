#app/admin/views.py
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
from . import admin
from forms import QrContentForm, QrSearchForm
from .. import db
from ..models import QRcode
from ..__init__ import db_session
#import create_qr_code
#from create_qr_code import create_qr
#import read_qr_code
#from read_qr_code import read_qr

def check_admin():
    """
    Prevent non-admins from accessing the page

    """
    if not current_user.is_admin:
        abort(403)

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

@admin.route('/qrcodes', methods=['GET', 'POST'])
@login_required
def list_qrcodes():
    """
    List all qrcodes

    """
    check_admin()

    qrcodes = QRcode.query.all()

    return render_template('admin/qrcodes/qrcodes.html', qrcodes=qrcodes, title= "QrCode Database")

@admin.route('/qrdatabase/add', methods=['GET', 'POST'])
@login_required
def add_qrcode():
    """
    Add a qrcode to the database

    """
    check_admin()

    add_qrcode = True

    form = QrContentForm(request.form)

    if request.method == 'POST' and form.validate():
        #save the qrcode
        qrcode = QRcode()
        save_changes(qrcode, form, new=True)
        flash('QrCode created successfully!')
        return redirect(url_for('admin.list_qrcodes'))
    """
    if form.validate_on_submit():
        qrcode = QRcode(name=form.name.data,
                        description=form.description.data,
                        qrcontent=create_qr(form.qrcontent.data))
       
        try:
            #add qrcode to the database
            db.session.add(qrcode)
            db.session.commmit()
            flash('You have successfully added a new QrCode.')
        except:
            #In case QrCode name already exists
            flash('Error: QrCode name already exists.')

        #Redirects to qrdatabase page
        return redirect(url_for('admin.list_qrcodes'))
        """
    #Load qrdatabase template
    return render_template('admin/qrcodes/qrcode.html', action="Add",
                           add_qrcode=add_qrcode, form=form,
                           title="Add QrCode")
"""
        db.session.add(qrcode)
        db.session.commit()
        flash('You have successfully added a new QrCode.')
        """

@admin.route('/qrdatabase/read/<int:id>', methods=['GET', 'POST'])
@login_required
def read_qrcode(id):
    """
    Read a qrcode in the database 

    """
    check_admin()

    results = []
    qry = db_session.query(QRcode).filter(QRcode.id==id)
    qrcode = qry.first()
    #decoded = QRcode(name=qrcode.name, description=qrcode.description, qrcontent=read_qr(qrcode.qrcontent))
    #results = decoded
    qrcode.qrcontent = read_qr(qrcode.qrcontent)
    results = qrcode

    if not results:
        flash('Content could not be read')
        return redirect(url_for('admin.list_qrcodes'))
    return render_template('admin/qrcodes/read.html', action="Read", 
                           results=results, title="QrCode Read")

@admin.route('/qrdatabase/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_qrcode(id):
    """
    Edit a qrcode

    """
    check_admin()

    edit_qrcode = True

    qry = db_session.query(QRcode).filter(QRcode.id==id)
    qrcode = qry.first()
    qrcode.qrcontent = qrcode.qrcontent.replace('http://api.qrserver.com/v1/create-qr-code/?data=', '')

    if qrcode:
        form = QrContentForm(formdata=request.form, obj=qrcode)
        if request.method == 'POST' and form.validate():
            #save edits
            save_changes(qrcode, form)
            flash('QrCode updated sucessfully!')
            return redirect(url_for('admin.list_qrcodes'))
        return render_template('admin/qrcodes/qrcode.html', action="Edit",
                           edit_qrcode=edit_qrcode, form=form,
                           qrcode=qrcode, title= "Edit QrCode")
    else:
        return 'Error loading #{id}'.format(id=id)
    """
    qrcode = QRcode.query.get_or_404(id)
    form = QrContentForm(obj=qrcode)
    if form.validate_on_submit():
        qrcode.name = form.name.data
        qrcode.description = form.description.data
        qrcode.qrcontent = create_qr(form.qrcontent.data)
        db.session.commit()
        flash('You have successfully edited the QrCode.')

        #Redirect to the qrdatabase page
        return redirect(url_for('admin.list_qrcodes'))

    form.qrcontent.data = qrcode.qrcontent
    form.description.data = qrcode.description
    form.name.data = qrcode.name
    """
    

@admin.route('/qrdatabase/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_qrcode(id):
    """
    Delete a qrcode from the database

    """
    check_admin()

    qrcode = QRcode.query.get_or_404(id)
    db.session.delete(qrcode)
    db.session.commit()
    flash('You have successfully deleted the QrCode.')

    #redirect to the qrdatabase page
    return redirect(url_for('admin.list_qrcodes'))
    
    return render_template(title="Delete QrCode")

@admin.route('/qrdatabase/search', methods=['GET', 'POST'])
@login_required
def search_qrcode():
    """ 
    Search a qrcode in the database

    """
    check_admin()

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
    
    return render_template('admin/qrcodes/search.html', action="Search",
                           form=search, title="QrCode Search")

@admin.route('/qrdatabase/results/', methods=['GET', 'POST'])
@login_required
def search_qrcode_results(search):

    check_admin()
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
        return redirect(url_for('admin.search_qrcode'))
    else:
        return render_template('admin/qrcodes/results.html', action="Results",
                               results=results, title="QrCode Results")


