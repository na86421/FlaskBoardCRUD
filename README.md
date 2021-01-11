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

```Python
#----------SignUp API----------
@bp_user.route('/signup', methods=['GET', 'POST'])  # 회원가입
def signup():  # POST를 이용해 db에 값 저장. SQLAlchemy ORM 쿼리 사용.
    if request.method == 'POST':
        try:
            new_user = User(id=request.form['id'],
                            password=bcrypt.generate_password_hash(request.form['password']).decode('utf-8'),
                            # 비밀번호를 암호화 하여 저장, UTF-8 디코딩 필수
                            name=request.form['name'],
                            email=request.form['email'])
            db.session.add(new_user)
            db.session.commit()
            flash("회원가입에 성공하셧습니다.")
            return render_template('login/login.html')
        except:
            flash("동일한 아이디는 사용할 수 없습니다.")
            return render_template('login/signup.html')
    return render_template('login/signup.html')


#----------Login API----------
@bp_user.route('/login', methods=['GET', 'POST'])  # 로그인
def login():
    if request.method == 'POST':
        id = request.form['id']
        password = request.form['password']
        try:

            user = User.query.filter_by(id=id).first() # 일치하는 id 쿼링
            check_pw = bcrypt.check_password_hash(user.password, password) # 패스워드 일치 여부 확인

            if user is not None and check_pw == True:  # 로그인 완료 시
                rd.set('id', id)  # redis server 에 세션(id 값, 로그온 사용자) 저장
                flash("로그인 하였습니다.")  # alert 메시지 전달
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


#----------Logout API----------
@bp_user.route('/logout')  # 로그아웃
def logout():
    rd.delete('id')  # 세션 삭제
    return render_template('login/login.html')
```

### Board API

```Python
#----------BoardRead API----------
@bp_board.route('/board')  # 게시판 리스트
def board():
    if rd.get('id') is not None:  # 로그온 시에만 게시판 접근 가능
        board_list = Board.query.filter(Board.title == '-1').order_by(Board.index.asc())
        recent_content = []  # 최근 게시글 쿼리 리스트
        for recents in board_list:  # 게시판의 갯수만큼 반복
            recent_content.append(  # 각 게시판의 최근 5개의 글 쿼링
                Board.query.filter(Board.title != '-1', Board.board_name == recents.board_name).order_by(
                    Board.date.desc()).limit(5))

        return render_template('board/board.html', board_list=board_list, recent_content=recent_content)
    else:  # 로그아웃 상태일 시 로그인 페이지로 이동
        return redirect('/login')


#----------BoardCreate API----------
@bp_board.route('/board_create', methods=['GET', 'POST'])  # 게시판 생성
def board_create():  # 게시판 생성 함수
    if rd.get('id') is not None:
        if request.method == 'POST':
            if rd.get('group') == None:  # 그룹_num 없을 경후 1 저장
                rd.set('group', 1)
            if int(rd.get('group')) > 10 : # 게시판은 10개로 제한
                flash("게시판은 10개 이상 생성할 수 없습니다.")
                return render_template('board/board_create.html')
            else :
                board_name = Board(board_name=request.form['board_name'], group=rd.get('group'), title='-1',
                                   name=rd.get('id'), text='-1', date=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                db.session.add(board_name)
                db.session.commit()
                rd.incr('group')  # 그룹_num 1 증가
                flash("게시판을 생성하였습니다.")
                return render_template('board/board_create.html')
        return render_template('board/board_create.html')
    else:
        return redirect('/login')


#----------BoardDelete API----------
@bp_board.route('/board_delete', methods=['GET', 'POST'])  # 게시판 삭제
def board_delete():  # 게시판 삭제 함수
    if rd.get('id') is not None:
        board_list = Board.query.filter(Board.title == '-1', Board.name == rd.get('id')).order_by(
            Board.index.asc())  # 게시판 삭제시 생성자만 삭제할 수 있게 쿼링
        page = request.args.get('page', type=int, default=1) # page default value = 1
        board_list = board_list.paginate(page, per_page=10) # pagination
        if request.method == 'POST':
            index = request.form.getlist('board_delete[]')
            for i in range(len(index)):  # 선택된 갯수만큼 삭제
                Board.query.filter(Board.index == index[i]).delete(synchronize_session='fetch')
            db.session.commit()
            flash("게시판을 삭제하였습니다.")
            return render_template('board/board_delete.html', board_list=board_list)

        return render_template('board/board_delete.html', board_list=board_list)
    else:
        return redirect('/login')


#----------BoardUpdate API----------
@bp_board.route('/board_edit')  # 게시판 수정 가능 리스트
def board_edit():
    if rd.get('id') is not None:
        board_list = Board.query.filter(Board.title == '-1', Board.name == rd.get('id')).order_by(Board.index.asc())
        page = request.args.get('page', type=int, default=1)
        board_list = board_list.paginate(page, per_page=10)
        return render_template('board/board_edit.html', board_list=board_list)
    else:
        return redirect('/login')


@bp_board.route('/board_edit/<index>', methods=['GET', 'POST'])  # 게시판 수정
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
                group_update.board_name = board_name  # 해당 게시판에 존재한 글의 board_name 같이 변경
            db.session.commit()
            flash("게시판 이름을 변경하였습니다.")
            return render_template('board/board_edit_name.html')

        board_list = Board.query.filter(Board.title == '-1', Board.index == index)
        return render_template('board/board_edit_name.html', index=index, board_list=board_list)
    else:
        return redirect('/login')
```

### BoardArticle API

```Python
#----------BoardArticle API----------
@bp_board.route('/board_detail/<board_name>/', methods=['GET', 'POST'])  #  글 리스트
def board_detail(board_name):
    if rd.get('id') is not None:
        # ----------BoardArticleRead API----------
        board_detail = Board.query.filter(Board.board_name == board_name, Board.title != '-1').order_by(
            Board.index.asc())
        page = request.args.get('page', type=int, default=1)
        board_detail = board_detail.paginate(page, per_page=10)

        # ----------BoardArticleUpdate API----------
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
                return render_template('board/content/board_detail.html', board_name=board_name,
                                       board_detail=board_detail)

        return render_template('board/content/board_detail.html', board_name=board_name, board_detail=board_detail)

    else:
        return redirect('/login')


@bp_board.route('/board_detail/<board_name>/<index>')  # 게시판 글 내용
def board_detail_content(board_name, index):
    if rd.get('id') is not None:
        # ----------BoardArticleRead API----------
        board_content = Board.query.filter(Board.board_name == board_name, Board.index == index)
        return render_template('board/content/board_content.html', board_name=board_name, board_content=board_content)

    else:
        return redirect('/login')


@bp_board.route('/board_detail/<board_name>/write', methods=['GET', 'POST'])  # 게시판 글 쓰기
def write(board_name):
    if rd.get('id') is not None:
        # ----------BoardArticleCreate API----------
        if request.method == 'POST':
            content_group = Board.query.filter(Board.board_name == board_name)
            for group in content_group:  # 글의 group 을 게시판의 group 과 일치시킴
                group_num = group.group
            content = Board(board_name=board_name, group=group_num, title=request.form['title'],
                            name=request.form['name'], text=request.form['text'],
                            date=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            db.session.add(content)
            db.session.commit()
            flash("글을 작성하였습니다.")
            return render_template('board/content/write.html', board_name=board_name)
        return render_template('board/content/write.html', board_name=board_name, id=rd.get('id'))

    else:
        return redirect('/login')


@bp_board.route('/board_detail/<board_name>/delete', methods=['GET', 'POST'])  # 게시판 글 삭제
def delete(board_name):
    if rd.get('id') is not None:
        # ----------BoardArticleDelete API----------
        board_detail = Board.query.filter(Board.board_name == board_name, Board.title != '-1',  # 글 삭제시 작성자만 삭제할 수 있게 쿼링
                                          Board.name == rd.get('id'))
        page = request.args.get('page', type=int, default=1)
        board_detail = board_detail.paginate(page, per_page=10)
        if request.method == 'POST':
            index = request.form.getlist('delete[]')
            for i in range(len(index)):
                Board.query.filter(Board.board_name == board_name, Board.index == index[i]).delete(synchronize_session='fetch')
            db.session.commit()
            flash("글을 삭제하였습니다.")
            return render_template('board/content/delete.html', board_name=board_name, board_detail=board_detail)
        return render_template('board/content/delete.html', board_name=board_name, board_detail=board_detail)

    else:
        return redirect('/login')
```
