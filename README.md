# Project Title / Flask Board CRUD

This service is a multi-board CURD

## Getting Started 

```
pip intsall -r requirements.txt
flask db init
flask db migrate
flask db run
```

### Prerequisites

```
alembic==1.4.3
bcrypt==3.2.0
cffi==1.14.4
click==7.1.2
dominate==2.6.0
Flask==1.1.2
Flask-Bcrypt==0.7.1
Flask-Migrate==2.5.3
Flask-SQLAlchemy==2.4.4
itsdangerous==1.1.0
Jinja2==2.11.2
Mako==1.1.3
MarkupSafe==1.1.1
psycopg2-binary==2.8.6
pycparser==2.20
python-dateutil==2.8.1
python-editor==1.0.4
redis==3.5.3
six==1.15.0
SQLAlchemy==1.3.22
visitor==0.1.3
Werkzeug==1.0.1
```


### Models.py

```Python
class User(db.Model):  # User 모델
    __tablename__ = 'user'

    id = db.Column(db.String, primary_key=True)
    password = db.Column(db.String())
    name = db.Column(db.String())
    email = db.Column(db.String())

    def __init__(self, id, password, name, email):
        self.id = id
        self.password = password
        self.name = name
        self.email = email

class Board(db.Model):  # 게시판 모델
    __tablename__ = 'board_list'

    index = db.Column(db.Integer, primary_key=True)
    board_name = db.Column(db.String)
    group = db.Column(db.Integer)
    title = db.Column(db.String)
    name = db.Column(db.String)
    text = db.Column(db.String)
    date = db.Column(db.TIMESTAMP)

    def __init__(self, board_name, group, title, name, text, date):
        self.board_name = board_name
        self.group = group
        self.title = title
        self.name = name
        self.text = text
        self.date = date
```

### User API

SignUp : Create a User.
Login : User logs in.
Logout : User logs out.


### Board API

Create : Create a Board.
Read : View Board lists.
Update : Change a Board name.
Delete : Delete a Board



### BoardArticle API

Create : Write a article.
Read : View article lists.
Update : Modify a article.
Delete : Delete a article.
