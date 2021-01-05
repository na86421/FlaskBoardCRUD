from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import redis
import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://root:root@localhost:5432/user"  # postgresql 연결
app.config["SECRET_KEY"] = "qng223^YT@g4@#$ga"

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
                flash("로그인 하였습니다.")
                return render_template('login/menu.html', id=rd.get('id'))
            else:
                flash("로그인 실패.")
                return render_template('login/login_fail.html')
        except:
            flash("로그인 실패.")
            return render_template('login/login_fail.html')

    if rd.get('id') is not None:  # 세션에 아이디(로그온)가 존재할 경우, 로그인 완료 페이지로 로딩.
        return render_template('login/menu.html', id=rd.get('id'))
    else:  # 세션에 아이디가 존재하지 않을 경우
        return render_template('login/login.html')


@app.route('/logout')  # 로그아웃
def logout():
    rd.delete('id')  # 세션 삭제
    return render_template('login/login.html')


@app.route('/board')  # 게시판
def board():
    if rd.get('id') is not None:  # 로그온 시에만 게시판 접근 가능
        board_list = Board.query.filter(Board.title == '-1').order_by(Board.index.asc())
        #cnt = board_list.count()
        recent_content = []
        for recents in board_list:
            recent_content.append(Board.query.filter(Board.title != '-1', Board.board_name == recents.board_name).order_by(Board.date.asc()).limit(5))
        print(recent_content[0])
        for i in recent_content[2]:
            print(i.title)
        page = request.args.get('page', type=int, default=1)
        board_list = board_list.paginate(page, per_page=10)

        #recent_content = Board.query.filter(Board.title != '-1').order_by(Board.date.asc()).limit(5*cnt)
        return render_template('board/board.html', board_list=board_list, recent_content=recent_content)
    else:  # 로그아웃 상태일 시 로그인 페이지로 이동
        return redirect('/login')


@app.route('/board_create', methods=['GET', 'POST'])  # 게시판 생성
def board_create():  # 게시판 생성 함수
    if rd.get('id') is not None:
        if request.method == 'POST':
            print(rd.get('group'))
            if rd.get('group') == None:  # 그룹_num 없을 경후 1 저장
                rd.set('group', 1)
            board_name = Board(board_name=request.form['board_name'], group=rd.get('group'), title='-1',
                               name=rd.get('id'), text='-1', date=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            db.session.add(board_name)
            db.session.commit()
            rd.incr('group')  # 그룹_num 1 증가
            flash("게시판을 생성하였습니다.")
            return render_template('board/board_create.html')
            #return redirect(url_for('board'))
        return render_template('board/board_create.html')
    else:
        return redirect('/login')


@app.route('/board_delete', methods=['GET', 'POST'])  # 게시판 삭제
def board_delete():  # 게시판 삭제 함수
    if rd.get('id') is not None:
        board_list = Board.query.filter(Board.title == '-1', Board.name == rd.get('id')).order_by(Board.index.asc())
        page = request.args.get('page', type=int, default=1)
        board_list = board_list.paginate(page, per_page=10)
        if request.method == 'POST':
            index = request.form.getlist('board_delete[]')
            for i in range(len(index)):
                Board.query.filter(Board.index == index[i]).delete()
            db.session.commit()
            flash("게시판을 삭제하였습니다.")
            return render_template('board/board_delete.html', board_list=board_list)
            #return redirect('/board_delete')

        return render_template('board/board_delete.html', board_list=board_list)
    else:
        return redirect('/login')


@app.route('/board_edit')  # 게시판 수정 가능 리스트
def board_edit():
    if rd.get('id') is not None:
        board_list = Board.query.filter(Board.title == '-1', Board.name == rd.get('id')).order_by(Board.index.asc())
        page = request.args.get('page', type=int, default=1)
        board_list = board_list.paginate(page, per_page=10)
        return render_template('board/board_edit.html', board_list=board_list)
    else:
        return redirect('/login')


@app.route('/board_edit/<index>', methods=['GET', 'POST'])  # 게시판 수정
def board_edit_index(index):  # 게시판 수정 함수
    if rd.get('id') is not None:
        if request.method == 'POST':
            board_name = request.form['board_name']
            board_edit_name = Board.query.filter(Board.index == index)  # 게시판 이름 변경 쿼리
            for update in board_edit_name:
                group = update.group
                update.board_name = board_name
            content_group = Board.query.filter(Board.group == group)  # 변경게시판의 그룹 넘버로 쿼링
            for group_update in content_group:
                group_update.board_name = board_name  # 해당 게시판에 존재한 글의 그룹도 같이 변경
            db.session.commit()
            flash("게시판 이름을 변경하였습니다.")
            return render_template('board/board_edit_name.html')
            #return redirect('/board_edit')

        board_list = Board.query.filter(Board.title == '-1', Board.index == index)
        return render_template('board/board_edit_name.html', index=index, board_list=board_list)
    else:
        return redirect('/login')


@app.route('/board_detail/<board_name>/', methods=['GET', 'POST'])  # 게시판 글 리스트
def board_detail(board_name):
    if rd.get('id') is not None:
        board_detail = Board.query.filter(Board.board_name == board_name, Board.title != '-1').order_by(
            Board.index.asc())
        page = request.args.get('page', type=int, default=1)
        board_detail = board_detail.paginate(page, per_page=10)
        print(board_detail)
        if request.method == 'POST':  # 게시판 글 수정
            title = request.form['title']
            text = request.form['text']
            index = request.form['index']
            equal_name = Board.query.filter(Board.board_name == board_name, Board.index == index,
                                            Board.name == rd.get('id')).scalar()  # 수정 가능 여부 확인 (글쓴이만 수정 가능)
            if equal_name is None:  # 글쓴이와 다를 경우
                flash("글쓴이가 아닐 경우 수정할 수 없습니다.")
                return render_template("board/content/write.html", board_name=board_name,
                                       board_detail=board_detail)
            else:  # 글쓴이와 동일
                content_update = Board.query.filter(Board.board_name == board_name, Board.index == index)
                for update in content_update:
                    update.title = title
                    update.text = text
                db.session.commit()
                flash("글을 수정하였습니다.")
                return render_template('board/content/board_detail.html', board_name=board_name, board_detail=board_detail)
                #return redirect('/board_detail/' + board_name + '/')

        return render_template('board/content/board_detail.html', board_name=board_name, board_detail=board_detail)

    else:
        return redirect('/login')


@app.route('/board_detail/<board_name>/<index>')  # 게시판 글 내용
def board_detail_content(board_name, index):
    if rd.get('id') is not None:
        board_content = Board.query.filter(Board.board_name == board_name, Board.index == index)
        return render_template('board/content/board_content.html', board_name=board_name, board_content=board_content)

    else:
        return redirect('/login')


@app.route('/board_detail/<board_name>/write', methods=['GET', 'POST'])  # 게시판 글 쓰기
def write(board_name):
    if rd.get('id') is not None:
        if request.method == 'POST':  # title, name, text, date
            content_group = Board.query.filter(Board.board_name == board_name)
            for group in content_group:  # 게시판 생성시 글의 group 을 게시판의 group 과 일치시킴
                group_num = group.group
            content = Board(board_name=board_name, group=group_num, title=request.form['title'],
                            name=request.form['name'], text=request.form['text'],
                            date=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            db.session.add(content)
            db.session.commit()
            flash("글을 작성하였습니다.")
            return render_template('board/content/write.html', board_name=board_name)
            #return redirect('/board_detail/' + board_name)
        return render_template('board/content/write.html', board_name=board_name, id=rd.get('id'))

    else:
        return redirect('/login')


@app.route('/board_detail/<board_name>/delete', methods=['GET', 'POST'])  # 게시판 글 삭제
def delete(board_name):
    if rd.get('id') is not None:
        board_detail = Board.query.filter(Board.board_name == board_name, Board.title != '-1',
                                          Board.name == rd.get('id'))
        page = request.args.get('page', type=int, default=1)
        board_detail = board_detail.paginate(page, per_page=10)
        if request.method == 'POST':
            index = request.form.getlist('delete[]')
            for i in range(len(index)):
                Board.query.filter(Board.board_name == board_name, Board.index == index[i]).delete()
            db.session.commit()
            flash("글을 삭제하였습니다.")
            return render_template('board/content/delete.html', board_name=board_name, board_detail=board_detail)
            #return redirect('/board_detail/' + board_name + '/delete')
        return render_template('board/content/delete.html', board_name=board_name, board_detail=board_detail)

    else:
        return redirect('/login')


if __name__ == '__main__':
    # app.secret_key = "qng223^YT@g4@#$ga"
    app.run(debug=True)
