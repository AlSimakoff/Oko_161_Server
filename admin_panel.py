# admin_panel.py
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from models import db, JournalBLog
from ImageModelView import ImageModelView

def init_admin(app):
    """Initialize admin panel."""
    #admin = Admin(app, name='My Admin', template_mode='bootstrap3')
    admin = Admin(app, name="MyApp", template_mode='bootstrap3')



    #admin.add_view(ModelView(JournalBLog, db.session))
    admin.add_view(ImageModelView(JournalBLog, db.session))