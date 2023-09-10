from app import db
from datetime import datetime,timedelta

# Expense model
class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    month = db.Column(db.String(9), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(90), nullable=False)

# Investments model
class Investments(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ticker = db.Column(db.String(5), nullable=False)

# Goals model
class Goal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    income = db.Column(db.Float, nullable=False)
    goal_price = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    description = db.Column(db.String(90), nullable=False)




