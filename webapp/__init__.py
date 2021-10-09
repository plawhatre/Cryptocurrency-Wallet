from flask import Flask
from webapp.blockchain import Blockchain
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_socketio import SocketIO

app = Flask(__name__)

app.config['SECRET_KEY'] = '$2b$12$1KkGNnE0B9CnM6Dgx1A5UuoqnROOf0hihhoKKt00S03RZHLcUNLKm'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['DOWNLOAD_FOLDER'] = 'DOWNLOAD_FOLDER'
app.config['UPLOAD_FOLDER'] = 'webapp/UPLOAD_FOLDER'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
socketio = SocketIO(app)

bc = Blockchain()

from webapp import routes