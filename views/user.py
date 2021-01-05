from flask import Blueprint, request, render_template, flash

from views import board
from app import db, rd
from models.models import User

bp_user = Blueprint('user', __name__, url_prefix='/') # 라우팅을 위한 것


@bp_user.route('/signup', methods=['GET', 'POST'])  # 회원가입
def signup():  # POST를 이용해 db에 값 저장. SQLAlchemy ORM 쿼리 사용.
    if request.method == 'POST':
        new_user = User(id=request.form['id'], password=request.form['password'], name=request.form['name'],
                        email=request.form['email'])
        db.session.add(new_user)
        db.session.commit()
        return render_template('login/login.html')
    return render_template('login/signup.html')


@bp_user.route('/login', methods=['GET', 'POST'])  # 로그인
def login():
    if request.method == 'POST':
        id = request.form['id']
        password = request.form['password']
        try:
            user = User.query.filter_by(id=id, password=password).first()
            if user is not None:  # 로그인 완료 시
                rd.set('id', id)  # redis server 에 세션(id 값, 로그온 사용자) 저장
                flash("로그인 하였습니다.") # alert 메시지 전달
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


@bp_user.route('/logout')  # 로그아웃
def logout():
    board.delete('id')  # 세션 삭제
    return render_template('login/login.html')
