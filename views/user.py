from flask import Blueprint, request, render_template, flash
from app import db, rd
from models.models import User
from app import bcrypt

bp_user = Blueprint('user', __name__, url_prefix='/')  # 라우팅을 위한 것

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
