from datetime import datetime
from webapp import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))

class User(db.Model, UserMixin):
	userid = db.Column(db.Integer, primary_key=True)
	
	username = db.Column(db.String(20), unique=True, nullable=False)
	usermail = db.Column(db.String(50), unique=True, nullable=False)
	userpwd = db.Column(db.String(50), nullable=False)
	userbal = db.Column(db.Float, nullable=False)
	usersk = db.Column(db.String(50), nullable=False)
	uservk = db.Column(db.String(50), nullable=False)
	activity = db.relationship('Transaction_history', backref='author', lazy=True)

	def __repr__(self):
		return f"This is a profile for user {self.username}"

	def get_id(self):
	           return (self.userid)

class Transaction_history(db.Model):
	tid = db.Column(db.Integer, primary_key=True)
	
	timestamp = db.Column(db.String(50), nullable=False)
	Action = db.Column(db.String(50), nullable=False)
	sender_address = db.Column(db.String(50), nullable=False)
	recipient_address = db.Column(db.String(50), nullable=False)
	amount = db.Column(db.Float, nullable=False)
	signature = db.Column(db.String(1000), nullable=False)
	userid = db.Column(db.Integer, db.ForeignKey('user.userid'), nullable=False)

class Transaction_pool(db.Model):
	tid = db.Column(db.Integer, primary_key=True)
	
	timestamp = db.Column(db.String(50), nullable=False)
	sender_address = db.Column(db.String(50), nullable=False)
	recipient_address = db.Column(db.String(50), nullable=False)
	amount = db.Column(db.Float, nullable=False)
	signature = db.Column(db.String(1000), nullable=False)
	userid = db.Column(db.Integer, db.ForeignKey('user.userid'), nullable=False)

class Notifications(db.Model):
	tid = db.Column(db.Integer, primary_key=True)
	
	timestamp = db.Column(db.String(50), nullable=False)
	sender_address = db.Column(db.String(50), nullable=False)
	recipient_address = db.Column(db.String(50), nullable=False)
	amount = db.Column(db.Float, nullable=False)
	userid = db.Column(db.Integer, db.ForeignKey('user.userid'), nullable=False)
