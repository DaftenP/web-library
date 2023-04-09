from flask import Blueprint, request, render_template, flash, redirect, url_for, session, g
from flask import current_app as app
from flask_paginate import Pagination, get_page_args
from app.module import dbModule

production = Blueprint('production', __name__, url_prefix='/')


@production.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        g.user = user_id


@production.route('/book/<code>', methods=['GET', 'POST'])
def book(code):
    db = dbModule.Database()
    sql1 = 'SELECT * FROM 도서 WHERE 도서_id = {0};'.format(code)
    sql2 = f'''SELECT 태그_태그명 as 태그명 FROM 태그'''
    sql3 = f'''SELECT A.*, B.회원_별명 FROM 리뷰 A LEFT JOIN 회원 B ON A.회원_id = B.회원_id WHERE 도서_id = {code};'''
    sql4 = f'''with tag_name as (select A.*, B.태그_태그명  from 리뷰태그 A left join 태그 B on A.태그_id = B.태그_id ) 
    SELECT A.리뷰_id as id, B.태그_태그명 as name, B.태그_id as tag FROM 리뷰 A left join tag_name B on A.리뷰_id = B.리뷰_id where A.도서_id = {code};'''

    row = db.executeAll(sql1)
    row2 = db.executeAll(sql2)
    row3 = db.executeAll(sql3)
    row4 = db.executeAll(sql4)
    tag = []
    for item in row2:
        tag.append(item['태그명'])
    if session.get('user_id') is not None:
        id = session['user_id']
        category = (row[0])['도서_카테고리']
        sql2 = f'''INSERT INTO 취향점수내역(취향점수내역_변동량, 취향점수내역_변동항목, 취향점수내역_변동근거, 회원_id) VALUES(1, "{category}", "상세보기", "{id}");'''
        sql3 = 'UPDATE 취향점수 SET ' + category + " = " + category + f' + 1 WHERE 회원_id = "{id}";'
        db.execute(sql2)
        db.execute(sql3)
        db.commit()
    if request.method == 'POST':
        if session.get('user_id') is not None:
            id = session['user_id']
            sql1 = 'SELECT count(*) as cnt FROM 장바구니항목 WHERE 회원_id = "{0}" and 도서_id = "{1}";'.format(id, code)
            cnt = db.executeAll(sql1)[0]['cnt']
            if cnt == 0:
                category = request.form.get('category')
                sql2 = 'INSERT INTO 장바구니항목(회원_id, 도서_id) VALUES("{0}","{1}");'.format(id, code)
                sql3 = f'''INSERT INTO 취향점수내역(취향점수내역_변동량, 취향점수내역_변동항목, 취향점수내역_변동근거, 회원_id) VALUES(10, "{category}", "장바구니", "{id}");'''
                sql4 = 'UPDATE 취향점수 SET ' + category + " = " + category + f' + 10 WHERE 회원_id = "{id}";'
                db.execute(sql2)
                db.execute(sql3)
                db.execute(sql4)
                db.commit()
                flash('장바구니에 추가되었습니다.')
            else:
                flash('이미 장바구니에 추가된 항목입니다.')
        else:
            flash('로그인 후 장바구니를 이용하실 수 있습니다.')
            return redirect(url_for('main.login'))

    return render_template('/main/book.html', row=row[0], tag=tag, review=row3, tags=row4)


@production.route('/basket', methods=['GET', 'POST'])
def basket():
    if session.get('user_id') is not None:
        id = session['user_id']
        db = dbModule.Database()
        if request.method == 'POST':
            for key, val in request.form.items():
                if val == 'on':
                    sql1 = 'DELETE FROM 장바구니항목 WHERE 회원_id = "{0}" AND 도서_id = "{1}";'.format(id, key)
                    db.execute(sql1)
                    db.commit()
        sql1 = 'SELECT * FROM 장바구니항목 A LEFT JOIN 도서 B ON A.도서_id = B.도서_id WHERE A.회원_id = "{0}";'.format(id)
        row = db.executeAll(sql1)
    else:
        flash('로그인 후 장바구니를 이용하실 수 있습니다.')
        return redirect(url_for('main.login'))

    return render_template('/main/basket.html', row=row)


@production.route('/purchase', methods=['GET', 'POST'])
def purchase():
    if session.get('user_id') is not None:
        id = session['user_id']
        db = dbModule.Database()
        if request.method == 'POST':
            if request.form.get('buy_once') == 'on':
                temp = request.form.get('book_code')
                sql1 = 'SELECT * FROM 도서 WHERE 도서_id = "{0}";'.format(temp)

            else:
                sql1 = 'SELECT * FROM 장바구니항목 A LEFT JOIN 도서 B ON A.도서_id = B.도서_id WHERE A.회원_id = "{0}";'.format(id)

            row = db.executeAll(sql1)
            sql2 = f'SELECT * FROM 배송지 WHERE 회원_id = "{id}";'
            sql3 = f'SELECT * FROM 신용카드 WHERE 회원_id = "{id}";'
            address = db.executeAll(sql2)
            card = db.executeAll(sql3)
    else:
        flash('로그인 후 이용하실 수 있습니다.')
        return redirect(url_for('main.login'))

    return render_template('/main/buy.html', row=row, address=address, card=card)


@production.route('/buy', methods=['GET', 'POST'])
def buy():
    if session.get('user_id') is not None:
        id = session['user_id']
        db = dbModule.Database()
        base_address = request.form.get('base_address')
        address = request.form.get('address')
        detail_address = request.form.get('detail_address')
        card_number = request.form.get('card_number')
        card_exp = request.form.get('card_exp')
        card_CVC = request.form.get('card_CVC')
        sum1 = int(request.form.get('sum'))

        sql1 = f'INSERT INTO 주문(회원_id, 주문총액, 주문_신용카드_CVC, 주문_신용카드_번호, 주문_신용카드_유효기간, 주문_우편번호, 주문_기본주소, 주문_상세주소) ' \
               f'VALUES("{id}", "{sum1}", "{card_CVC}", "{card_number}", "{card_exp}", "{address}", "{base_address}", "{detail_address}");'
        sql2 = f'SELECT 주문_id as num FROM 주문 WHERE 회원_id = "{id}" ORDER BY 주문_id DESC LIMIT 1;'

        db.execute(sql1)
        db.commit()
        order_num = int(db.executeAll(sql2)[0]['num'])

        for key, val in request.form.items():
            print(key, val)
            if key == 'sum': break
            sql3 = f'INSERT INTO 주문항목(주문_id, 도서_id, 주문항목_수량) VALUES("{order_num}", "{key}", "{val}");'
            sql4 = f'''SELECT 도서_카테고리 as category FROM 도서 WHERE 도서_id = "{key}";'''
            category = (db.executeAll(sql4)[0])['category']
            sql5 = f'''INSERT INTO 취향점수내역(취향점수내역_변동량, 취향점수내역_변동항목, 취향점수내역_변동근거, 회원_id) VALUES(50, "{category}", "구매", "{id}");'''
            sql6 = 'UPDATE 취향점수 SET ' + category + " = " + category + f' + 50 WHERE 회원_id = "{id}";'
            db.execute(sql3)
            db.execute(sql5)
            db.execute(sql6)
        db.commit()
        return redirect(url_for('main.index'))
    else:
        flash('로그인 후 이용하실 수 있습니다.')
        return redirect(url_for('main.login'))


@production.route('/book_registration', methods=['GET', 'POST'])
def book_registration():
    db = dbModule.Database()
    sql1 = f'''SELECT 태그_태그명 as 태그명 FROM 태그'''
    row = db.executeAll(sql1)
    tag = []
    for item in row:
        tag.append(item['태그명'])
    if request.method == 'POST':
        rst = []
        for key, val in request.form.items():
            rst.append(val)
        sql1 = f'''INSERT INTO 도서 VALUES({int(rst[0])}, "{rst[1]}", 500, {int(rst[2])}, "{rst[3]}", 0, 0, 0, "{rst[4]}", "{rst[5]}", "{rst[6]}", "{rst[7]}");'''
        db.execute(sql1)
        db.commit()
        tag_id = []
        for i in range(8, len(rst)):
            sql3 = f'''SELECT 태그_id FROM 태그 WHERE 태그_태그명 = "{rst[i]}";'''
            temp = db.executeAll(sql3)
            if len(temp) == 0:
                sql4 = f'''INSERT INTO 태그(태그_태그명) VALUES("{rst[i]}")'''
                db.execute(sql4)
                db.commit()
            temp = db.executeAll(sql3)
            tag_id.append((temp[0])['태그_id'])
        for tag in tag_id:
            sql5 = f'''INSERT INTO 기본태그 VALUES({int(tag)}, {int(rst[0])});'''
            sql6 = f'''UPDATE 태그 SET 태그_태그수 = 태그_태그수 + 1 WHERE 태그_id = "{tag}";'''
            db.execute(sql5)
            db.execute(sql6)
        db.commit()
        return redirect(url_for('production.book_registration'))
    return render_template('/main/book_registration.html', tag=tag)

