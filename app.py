from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import redis
import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://root:root@localhost:5432/user"  # postgresql 연결

rd = redis.Redis(host='localhost', port=6379, db=0, charset="utf-8", decode_responses=True)  # redis server 연결

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


class Board(db.Model):  # 게시판 클래스
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
        return render_template('login/login.html')
    return render_template('login/signup.html')


@app.route('/login', methods=['GET', 'POST'])  # 로그인
def login():
    if request.method == 'POST':
        id = request.form['id']
        password = request.form['password']
        try:
            user = User.query.filter_by(id=id, password=password).first()
            if user is not None:  # 로그인 완료 시
                rd.set('id', id)  # redis server 에 세션 저장
                return render_template('login/menu.html', id=rd.get('id'))
            else:  # id 틀림
                return '로그인 실패'
        except:  # 페스워드 틀릴
            return '로그인 실패'
    return render_template('login/login.html')


@app.route('/logout')  # 로그아웃
def logout():
    rd.delete('id')  # 세션 삭제
    return render_template('login/login.html')


@app.route('/board')  # 게시판
def board():
    board_list = Board.query.filter(Board.title == '-1').order_by(Board.index.asc())

    return render_template('board/board.html', board_list=board_list)


@app.route('/board_create', methods=['GET', 'POST'])  # 게시판 생성
def board_create():  # 게시판 생성 함수
    if request.method == 'POST':
        board_name = Board(board_name=request.form['board_name'], title='-1',
                           name='-1', text='-1', date=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        db.session.add(board_name)
        db.session.commit()
        return redirect(url_for('board'))
    return render_template('board/board_create.html')


@app.route('/board_delete', methods=['GET', 'POST'])  # 게시판 삭제
def board_delete():  # 게시판 삭제 함수
    if request.method == 'POST':
        index = request.form.getlist('board_delete[]')
        for i in range(len(index)):
            Board.query.filter(Board.index == index[i]).delete()
        db.session.commit()
        return redirect('/board_delete')

    board_list = Board.query.filter(Board.title == '-1').order_by(Board.index.asc())
    return render_template('board/board_delete.html', board_list=board_list)


@app.route('/board_edit')  # 게시판 수정 가능 리스트
def board_edit():
    board_list = Board.query.filter(Board.title == '-1').order_by(Board.index.asc())
    return render_template('board/board_edit.html', board_list=board_list)


@app.route('/board_edit/<index>', methods=['GET', 'POST'])  # 게시판 수정
def board_edit_index(index):  # 게시판 수정 함수
    if request.method == 'POST':
        board_name = request.form['board_name']
        board_edit_name = Board.query.filter(Board.index == index)
        for update in board_edit_name:
            update.board_name = board_name
        db.session.commit()
        return redirect('/board_edit')

    board_list = Board.query.filter(Board.title == '-1', Board.index == index)
    return render_template('board/board_edit_name.html', index=index, board_list=board_list)


@app.route('/board_detail/<board_name>/', methods=['GET', 'POST'])  # 게시판 글 리스트
def board_detail(board_name):
    if request.method == 'POST':  # 게시판 글 수정
        title = request.form['title']
        text = request.form['text']
        index = request.form['index']
        content_update = Board.query.filter(Board.board_name == board_name, Board.index == index)
        for update in content_update:
            update.title = title
            update.text = text
        db.session.commit()
        return redirect('/board_detail/' + board_name + '/')

    board_detail = Board.query.filter(Board.board_name == board_name, Board.title != '-1')
    return render_template('board/content/board_detail.html', board_name=board_name, board_detail=board_detail)


@app.route('/board_detail/<board_name>/<index>')  # 게시판 글 내용
def board_detail_content(board_name, index):
    board_content = Board.query.filter(Board.board_name == board_name, Board.index == index)
    return render_template('board/content/board_content.html', board_name=board_name, board_content=board_content)


@app.route('/board_detail/<board_name>/write', methods=['GET', 'POST'])  # 게시판 글 쓰기
def write(board_name):
    if request.method == 'POST':  # title, name, text, date
        content = Board(board_name=board_name, title=request.form['title'],
                        name=request.form['name'], text=request.form['text'],
                        date=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        db.session.add(content)
        db.session.commit()
        return redirect('/board_detail/' + board_name)
    return render_template('board/content/write.html', board_name=board_name, id=rd.get('id'))


@app.route('/board_detail/<board_name>/delete', methods=['GET', 'POST'])  # 게시판 글 삭제
def delete(board_name):
    if request.method == 'POST':
        index = request.form.getlist('delete[]')
        for i in range(len(index)):
            Board.query.filter(Board.board_name == board_name, Board.index == index[i]).delete()
        db.session.commit()
        return redirect('/board_detail/' + board_name + '/delete')
    board_detail = Board.query.filter(Board.board_name == board_name, Board.title != '-1')
    return render_template('board/content/delete.html', board_name=board_name, board_detail=board_detail)


if __name__ == '__main__':
    app.run(debug=True)
    # app.secret_key = "test"
