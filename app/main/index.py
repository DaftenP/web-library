from flask import Blueprint, request, render_template, flash, redirect, url_for, session, g
from flask import current_app as app
from app.module import dbModule

# 추가할 모듈이 있다면 추가

main = Blueprint('main', __name__, url_prefix='/')

@main.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        g.user = user_id

@main.route('/', methods=['GET'])
def index():

    return render_template('/main/index.html')


@main.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        db = dbModule.Database()
        rst = request.form
        id = str(rst['id'])
        pw = str(rst['pw'])
        sql1 = 'INSERT INTO 회원(회원_id, 비밀번호) VALUES("%s","%s");' % (id, pw)
        db.execute(sql1)
        db.commit()
        return redirect(url_for('main.index'))

    return render_template('/main/signup.html')


@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        db = dbModule.Database()
        rst = request.form
        id = str(rst['id'])
        pw = str(rst['pw'])
        sql2 = 'SELECT 회원_id, 비밀번호 FROM 회원 WHERE 회원_id = "{0}";'.format(id)
        row = db.executeAll(sql2)
        print(row)
        if len(row) != 0 and row[0]['비밀번호'] == pw :
            session.clear()
            session['user_id'] = id
            return redirect(url_for('main.index'))

    return render_template('/main/login.html')


@main.route('/logout', methods=['GET', 'POST'])
def logout():
    session.clear()
    return redirect(url_for('main.index'))