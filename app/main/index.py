from flask import Blueprint, request, render_template, flash, redirect, url_for, session, g
from flask import current_app as app
from flask_paginate import Pagination, get_page_args
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
    per_page = 4

    db = dbModule.Database()
    page, _, offset = get_page_args(per_page=per_page)
    data = []
    taste = []
    if session.get('user_id') is None:
        sql1 = 'SELECT count(*) FROM 도서;'
        sql2 = 'SELECT * FROM 도서 LIMIT {0} OFFSET {1};'.format(per_page, offset)
    else:
        id = session.get('user_id')
        sql3 = f'SELECT 소설, 인문, 역사, 종교, 어린이, 만화, 자기계발, 경제, 청소년, 여행, 잡지, 대학교재, 취미 FROM 취향점수 WHERE 회원_id = "{id}";'
        row = db.executeAll(sql3)[0]
        data = sorted(row.items(), key=lambda x: x[1], reverse=True)
        sql1 = f'SELECT count(*) FROM 도서 WHERE 도서_카테고리 IN ("{data[0][0]}", "{data[1][0]}", "{data[2][0]}");'
        sql2 = f'SELECT * FROM 도서 WHERE 도서_카테고리 IN ("{data[0][0]}", "{data[1][0]}", "{data[2][0]}") LIMIT {per_page} OFFSET {offset};'
        for key, val in data :
            taste.append(key)

    total = db.executeAll(sql1)[0]['count(*)']
    row = db.executeAll(sql2)
    return render_template('/main/index.html', row=row,
                           pagination=Pagination(
                               page=page,
                               total=total,
                               per_page=per_page,
                               bs_version=5,
                               show_single_page=True),
                           taste=taste)


@main.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        db = dbModule.Database()
        rst = request.form.items()
        lst = []
        for key, val in rst:
            lst.append(val)
        sql1 = f'INSERT INTO 회원(회원_이름, 회원_별명, 회원_id, 비밀번호, 회원_이메일, 회원_생년월일) VALUES("{lst[0]}","{lst[1]}","{lst[2]}","{lst[3]}", "{lst[4]}","{lst[5]}");'
        sql2 = f'INSERT INTO 취향점수(회원_id) VALUES("{lst[2]}");'
        db.execute(sql1)
        db.execute(sql2)
        db.commit()
        for i in range(6, 9):
            sql3 = 'UPDATE 취향점수 SET ' + f"{lst[i]}" + ' = ' + f"{lst[i]}" + f' + 20 WHERE 회원_id = "{lst[2]}";'
            db.execute(sql3)
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
        sql1 = 'SELECT 회원_id, 비밀번호 FROM 회원 WHERE 회원_id = "{0}";'.format(id)
        row = db.executeAll(sql1)
        if len(row) != 0 and row[0]['비밀번호'] == pw:
            session.clear()
            session['user_id'] = id
            return redirect(url_for('main.index'))

    return render_template('/main/login.html')


@main.route('/logout', methods=['GET', 'POST'])
def logout():
    session.clear()
    return redirect(url_for('main.index'))


@main.route('/search/<code>', methods=['GET', 'POST'])
def search(code):
    db = dbModule.Database()
    if code == 'norm':
        keyword = request.form.get('keyword')
        if session.get('user_id') is not None:
            id = session['user_id']
            sql1 = f'INSERT INTO 검색어로그(회원_id, 검색어로그_검색어) VALUES("{id}", "{keyword}");'
        else:
            sql1 = f'INSERT INTO 검색어로그(검색어로그_검색어) VALUES("{keyword}");'
        db.execute(sql1)
        db.commit()
        sql2 = f'SELECT * FROM 도서 WHERE 도서_도서명 LIKE "%%{keyword}%%";'
        row = db.executeAll(sql2)
    else:
        sql1 = f'''SELECT * FROM 도서 WHERE 도서_id IN (SELECT B.도서_id FROM 리뷰태그 A LEFT JOIN 리뷰 B ON A.리뷰_id = B.리뷰_id WHERE A.태그_id = {code});'''
        row = db.executeAll(sql1)

    return render_template('/main/booklist.html', row=row)


@main.route('/orders', methods=['GET', 'POST'])
def orders():
    if session.get('user_id') is not None:
        id = session['user_id']
        db = dbModule.Database()
        sql1 = f'SELECT * FROM 주문 WHERE 회원_id = "{id}";'
        row = db.executeAll(sql1)
    else:
        flash('로그인 후 이용하실 수 있습니다.')
        return redirect(url_for('main.login'))
    return render_template('/main/orderlist.html', row=row)


@main.route('/orderitems/<code>', methods=['GET', 'POST'])
def orderitems(code):
    if session.get('user_id') is not None:
        db = dbModule.Database()
        sql1 = f'SELECT * FROM 주문항목 A LEFT JOIN 도서 B ON A.도서_id = B.도서_id WHERE 주문_id = "{code}";'
        row = db.executeAll(sql1)
    else:
        flash('로그인 후 이용하실 수 있습니다.')
        return redirect(url_for('main.login'))
    return render_template('/main/order_detail.html', row=row)


@main.route('/mypage', methods=['GET', 'POST'])
def mypage():
    if session.get('user_id') is not None:
        db = dbModule.Database()
        id = session['user_id']
        if request.method == 'POST':
            rst = request.form
            if rst.get('address_name'):
                # sql4 = f'SELECT count(*) as cnt FROM 배송지 WHERE 회원_id = "{id}";'
                sql3 = f'''INSERT INTO 배송지(회원_id, 우편번호, 배송지_기본주소, 배송지_상세주소, 배송지_별명) VALUES("{id}", "{rst['address']}", "{rst['base_address']}", "{rst['detail_address']}", "{rst['address_name']}");'''
                db.execute(sql3)
                db.commit()
            if rst.get('card_num'):
                sql3 = f'''INSERT INTO 신용카드 VALUES("{rst['card_num']}", "{id}", "{rst['card_exp']}", "{rst['card_name']}", "{rst['CVC']}");'''
                db.execute(sql3)
                db.commit()
            if rst.get('address_id'):
                sql3 = f'''DELETE FROM 배송지 WHERE 배송지_id = "{rst['address_id']}";'''
                db.execute(sql3)
                db.commit()
            if rst.get('card_id'):
                sql3 = f'''DELETE FROM 신용카드 WHERE 신용카드_번호 = "{rst['card_id']}";'''
                db.execute(sql3)
                db.commit()
        sql1 = f'SELECT * FROM 배송지 WHERE 회원_id = "{id}";'
        sql2 = f'SELECT * FROM 신용카드 WHERE 회원_id = "{id}";'

        row1 = db.executeAll(sql1)
        row2 = db.executeAll(sql2)

    else:
        flash('로그인 후 이용하실 수 있습니다.')
        return redirect(url_for('main.login'))
    return render_template('/main/registration.html', row1=row1, row2=row2)


@main.route('/review_send/<code>', methods=['GET', 'POST'])
def review_send(code):
    if session.get('user_id') is not None:
        db = dbModule.Database()
        id = session['user_id']
        if request.method == 'POST':
            rst = []
            for _, val in request.form.items():
                rst.append(val)
            sql1 = f'''INSERT INTO 리뷰(회원_id, 도서_id, 리뷰_내용, 리뷰_평점) VALUES("{id}", "{code}", "{rst[0]}", {int(rst[1])});'''
            sql2 = f'''SELECT 리뷰_id FROM 리뷰 WHERE 회원_id = "{id}" and 도서_id = "{code}" ORDER BY 리뷰_id DESC;'''
            db.execute(sql1)
            db.commit()
            review_id = (db.executeAll(sql2)[0])['리뷰_id']
            tag_id = []
            for i in range(2, len(rst)):
                sql3 = f'''SELECT 태그_id FROM 태그 WHERE 태그_태그명 = "{rst[i]}";'''
                temp = db.executeAll(sql3)
                if len(temp) == 0:
                    sql4 = f'''INSERT INTO 태그(태그_태그명) VALUES("{rst[i]}")'''
                    db.execute(sql4)
                    db.commit()
                temp = db.executeAll(sql3)
                tag_id.append((temp[0])['태그_id'])
            for tag in tag_id:
                sql5 = f'''INSERT INTO 리뷰태그(리뷰_id, 태그_id) VALUES({int(review_id)}, {int(tag)});'''
                sql6 = f'''UPDATE 태그 SET 태그_태그수 = 태그_태그수 + 1 WHERE 태그_id = "{tag}";'''
                db.execute(sql5)
                db.execute(sql6)
                db.commit()

    return redirect(url_for('production.book', code=code))


@main.route('/tag_rank', methods=['GET', 'POST'])
def tag_rank():
    return render_template('/main/mytag.html')