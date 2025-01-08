# admin_panel.py
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from models import db, JournalBLog

def init_admin(app):
    """Initialize admin panel."""
    admin = Admin(app, name='My Admin', template_mode='bootstrap3')
    admin.add_view(ModelView(JournalBLog, db.session))