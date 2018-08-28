from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class BaseModel(db.Model):
    __abstract__ = True

    created_on = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow()
    )
    updated_on = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow(),
        onupdate=datetime.utcnow()
    )

class Bounter(BaseModel):
    __Tablename__ = "Bounter"
    id = db.Column(db.Integer, primary_key=True)
    telegram_id = db.Column(db.Integer, unique=True)
    telegram_username = db.Column(db.String(40))
    telegram_name = db.Column(db.String(40))
    number_of_weeks_completed = db.Column(db.Integer)
    last_break_point = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow()
    )
    is_active_bounter = db.Column(db.Boolean(), default=False)
    in_google_sheet = db.Column(db.Boolean(), default=False)
    eth_address = db.Column(db.String(60))

    def __init__(self, tid, t_name, t_username=""):
        self.telegram_id = tid
        self.telegram_username = t_username
        self.telegram_name = t_name
        self.number_of_weeks_completed = 0
        self.is_active_bounter = False

    

    

    def __str__(self):
        return f'''
<id: {self.telegram_id}, name: {self.telegram_name}
username: {self.telegram_username} active bounter: {self.is_active_bounter} >'''
    
    @staticmethod
    def get_bounter(telegram_id=None, telegram_name=None, telegram_username=None):
        if telegram_id:
            return Bounter.query.filter_by(telegram_id=telegram_id).first()
        if telegram_name:
            return Bounter.query.filter_by(telegram_name=telegram_name).first()
        if telegram_username:
            return Bounter.query.filter_by(telegram_username=telegram_username).first()
        return None
    
    @staticmethod
    def break_point(telegram_id, update_week=False):
        user = Bounter.get_bounter(telegram_id=telegram_id)
        if not user:
            return
        if update_week and user.is_active_bounter:
            user.number_of_weeks_completed = Bounter.get_wks(user)
        user.last_break_point = datetime.utcnow()
        return True

    @staticmethod
    def set_is_active_bounter(telegram_id, is_active):
        user = Bounter.get_bounter(telegram_id=telegram_id)
        user.is_active_bounter = is_active

    @staticmethod
    def add_bounter(tid, t_name, t_username=""):
        new_bounter = Bounter(tid, t_name, t_username)
        db_add(new_bounter)
        return new_bounter

    @staticmethod
    def get_wks(user):
        t_diff = datetime.utcnow() - user.last_break_point
        #return user.number_of_weeks_completed + ((t_diff.seconds / 60) // 2)
        return user.number_of_weeks_completed + (t_diff.days // 7)

#some functions

def db_commit():
    db.session.commit()

def db_add(obj):
    db.session.add(obj)
