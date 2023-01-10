from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager


from config import Config

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
manager = LoginManager(app)

from app.models import Blog
from . import routes
