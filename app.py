from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import redis

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://root:root@localhost:5432/user"  # postgresql 연결
app.config["SECRET_KEY"] = "qng223^YT@g4@#$ga"  # 암호화 key, flash 이

rd = redis.Redis(host='localhost', port=6379, db=0, charset="utf-8", decode_responses=True)  # redis server 연결

db = SQLAlchemy(app)
migrate = Migrate(app, db)  # migrate

from views.user import bp_user
from views.board import bp_board
from views.index import bp_index

app.register_blueprint(bp_user)  # bluteprint 이용 route 구성
app.register_blueprint(bp_board)
app.register_blueprint(bp_index)

if __name__ == '__main__':
    app.run(debug=True)
