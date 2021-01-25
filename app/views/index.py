from flask import render_template, Blueprint

bp_index = Blueprint('index', __name__, url_prefix='/')


@bp_index.route('/')  # 인덱스
def index():
    return render_template('index.html')
