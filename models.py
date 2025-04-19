from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class JournalBLog(db.Model):
    __tablename__ = 'bolshoilog_img'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    time = db.Column(db.String(50), nullable=False)
    color = db.Column(db.String(50), nullable=False)
    license_number = db.Column(db.String(50), nullable=False)
    type_auto = db.Column(db.String(50), nullable=False)
    img_plate_url = db.Column(db.String(255), nullable=True)
    img_car_url = db.Column(db.String(255), nullable=True)
