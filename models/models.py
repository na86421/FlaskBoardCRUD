from app import db


class User(db.Model):  # User 클래스
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


class Board(db.Model):  # 게시판 클래스
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
