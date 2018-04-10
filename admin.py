import os 

#Local imports
from app import create_app


config_name = os.getenv('FLASK_CONFIG')
app = create_app(config_name)
app.app_context().push()


from app.models import User
from app import db
admin = User(email="admin@admin.com",username="admin",password="admin2018",is_admin=True)
db.session.add(admin)
db.session.commit()
