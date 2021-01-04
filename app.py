from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import Sequence
import redis
import datetime

# nowDatetime = now.strftime('%Y-%m-%d %H:%M:%S')
# print(nowDatetime)  # 2015-04-19 12:11:32

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://root:root@localhost:5432/user"

rd = redis.Redis(host='localhost', port=6379, db=0, charset="utf-8", decode_responses=True)

db = SQLAlchemy(app)
migrate = Migrate(app, db)


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


class Board(db.Model):  # 게시판 리스트 클래스
    __tablename__ = 'board_list'

    index = db.Column(db.Integer, primary_key=True)
    board_name = db.Column(db.String)
    title = db.Column(db.String)
    name = db.Column(db.String)
    text = db.Column(db.String)
    date = db.Column(db.TIMESTAMP)

    def __init__(self, board_name, title, name, text, date):
        self.board_name = board_name
        self.title = title
        self.name = name
        self.text = text
        self.date = date


@app.route('/')  # 인덱스
def index():
    return render_template('index.html')


@app.route('/signup', methods=['GET', 'POST'])  # 회원가입
def signup():  # POST를 이용해 db에 값 저장. SQLAlchemy ORM 쿼리 사용.
    if request.method == 'POST':
        new_user = User(id=request.form['id'], password=request.form['password'], name=request.form['name'],
                        email=request.form['email'])
        db.session.add(new_user)
        db.session.commit()
        return render_template('login.html')
    return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        id = request.form['id']
        password = request.form['password']
        try:
            user = User.query.filter_by(id=id, password=password).first()
            if user is not None:  # 로그인 완료 시
                rd.set('id', id)  # redis server 에 세션 저장
                return render_template('menu.html', id=rd.get('id'))
            else:  # id 틀림
                return '로그인 실패'
        except:  # 페스워드 틀릴
            return '로그인 실패'
    return render_template('login.html')


@app.route('/logout')
def logout():
    rd.delete('id')  # 세션 삭제
    return render_template('login.html')


@app.route('/board')
def board():
    board_list = Board.query.filter(Board.title == '-1')

    return render_template('board.html', board_list=board_list)


@app.route('/board_create', methods=['GET', 'POST'])
def board_create():  # 게시판 생성 함수
    if request.method == 'POST':
        board_name = Board(board_name=request.form['board_name'], title='-1',
                           name='-1', text='-1', date=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        db.session.add(board_name)
        db.session.commit()
        return redirect(url_for('board'))
    return render_template('board_create.html')


@app.route('/board_detail/<board_name>/', methods=['GET', 'POST'])
def board_detail(board_name):
    if request.method == 'POST':
        title = request.form['title']
        text = request.form['text']
        board_update = Board.query.filter(Board.board_name == board_name, Board.index == request.form['index'])
        for update in board_update:
            update.title = title
            update.text = text
        db.session.commit()
        return redirect('/board_detail/'+board_name+'/')

    board_detail = Board.query.filter(Board.board_name == board_name, Board.title != '-1')
    return render_template('board_detail.html', board_name=board_name, board_detail=board_detail)


@app.route('/board_detail/<board_name>/<index>')
def board_detail_content(board_name, index):
    board_content = Board.query.filter(Board.board_name == board_name, Board.index == index)
    return render_template('board_content.html', board_name=board_name, board_content=board_content)


@app.route('/board_detail/<board_name>/write', methods=['GET', 'POST'])
def write(board_name):
    if request.method == 'POST':  # title, name, text, date
        content = Board(board_name=board_name, title=request.form['title'],
                        name=request.form['name'], text=request.form['text'],
                        date=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        db.session.add(content)
        db.session.commit()
        return redirect('/board_detail/' + board_name)
    return render_template('write.html', board_name=board_name, id=rd.get('id'))


if __name__ == '__main__':
    app.run(debug=True)
    # app.secret_key = "test"
