"""
Flask extensions are instantiated here (without an app) and initialized
later inside create_app(). This avoids circular imports between
app.py, models, and routes.
"""

from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_cors import CORS

db = SQLAlchemy()
bcrypt = Bcrypt()
jwt = JWTManager()
cors = CORS()
