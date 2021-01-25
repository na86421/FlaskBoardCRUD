# Import flask
from flask import Flask

# Import SQLAlchemy
from flask_sqlalchemy import SQLAlchemy

# Import Redis
import redis

# Import Migrate
from flask_migrate import Migrate

# Import Bcrypt
from flask_bcrypt import Bcrypt

# Define the WSGI application object
app = Flask(__name__)

# Configurations
app.config.from_object('config')

# Define the database object which is imported
# by modules and controllers
db = SQLAlchemy(app)

# Define Migrate
migrate = Migrate(app, db)  # migrate

# Define Bcrypt
bcrypt = Bcrypt(app)

# Define Redis server
rd = redis.Redis(host='localhost', port=6379, db=0, charset="utf-8", decode_responses=True)

# Import a module / component using its blueprint handler variable

from app.views.user import bp_user
from app.views.board import bp_board
from app.views.index import bp_index

# Register blueprint(s)
app.register_blueprint(bp_user)  # blueprint 이용 route 구성
app.register_blueprint(bp_board)
app.register_blueprint(bp_index)

# Build the database: # This will create the database file using SQLAlchemy
db.create_all()
