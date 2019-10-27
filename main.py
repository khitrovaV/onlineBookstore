from flask import Flask, render_template, redirect, url_for, request, make_response
from model import *
from auth import Auth
from sqlalchemy import or_
import hashlib

app = Flask(__name__)

SQLALCHEMY_TRACK_MODIFICATIONS = False

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data/store.db'
db.init_app(app)
auth = Auth()


@app.route("/", methods=['GET', 'POST'])
def hello():
    if request.method == 'GET':
        db_data = Book.query.all()
        if not auth.isLoggedUser(request.cookies):
            return render_template('fields.html', db_data=db_data, auth=False, css_url=url_for('static', filename='css/style.css'))
        client = Client.query.get(request.cookies.get('client_login'))
        return render_template('fields.html', db_data=db_data, auth=True, client=client, css_url=url_for('static', filename='css/style.css'))


@app.route("/find", methods=['GET'])
def find():
    if request.method == 'GET':
        st = False
        if auth.isLoggedUser(request.cookies):
            st = True
        client = Client.query.get(request.cookies.get('client_login'))
        finded_value = request.args.get('finded_value')
        if not request.args.get('finded_value'):
            return redirect(url_for('hello'))
        else:
            db_data = Book.query.filter(Book.name.ilike("%{}%".format(finded_value))).all()
            return render_template('fields.html', db_data=db_data, auth=st, client=client, css_url=url_for('static', filename='css/style.css'))


@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('auth.html')

    elif request.method == 'POST':
        if auth.login(request.form.get('login'), request.form.get('password')):
            resp = make_response(redirect(url_for('hello')))
            h = hashlib.sha1(str.encode(request.form.get('password')))
            p = h.hexdigest()
            resp.set_cookie('userID', p)
            resp.set_cookie('client_login', request.form.get('login'))
            return resp
        else:
            return render_template('auth.html', errors=['Не верный логин или пароль'])


@app.route("/registration", methods=['GET', 'POST'])
def registration():
    if request.method == 'GET':
        return render_template('registration.html')

    elif request.method == 'POST':
        if auth.validate(request.form):
            client = Client(request.form.get('login'), request.form.get('password'), request.form.get('fio'), request.form.get('address'))
            db.session.add(client)
            db.session.commit()
            return redirect(url_for('login'))
        else:
            return render_template('registration.html', errors=['Данные введены не верно'])


@app.route("/basket", methods=['GET', 'POST'])
def basket():
    if request.method == 'GET':
        st = False
        if auth.isLoggedUser(request.cookies):
            st = True
            client = Client.query.get(request.cookies.get('client_login'))
        db_data = Book.query.filter(Book.book_id == Basket.book_id).filter(Basket.client_login == client.client_login)
        return render_template('basket.html', db_data=db_data,  auth=st, client=client, css_url=url_for('static', filename='css/style.css'))


@app.route("/add_book/<book_id>", methods=['GET', 'POST'])
def addBook(book_id=None):
    if request.method == 'GET':
        add = Basket.query.filter(Basket.book_id == book_id).filter(Basket.client_login == request.cookies.get('client_login')).first()
        if add:
            add.number += int(request.args.get('count'))
        elif not add:
            add_book = Basket(request.cookies.get('client_login'), book_id, request.args.get('count'))
            db.session.add(add_book)
        db.session.commit()
        return redirect(url_for("hello"))


@app.route("/delete_book/<book_id>", methods=['GET', 'POST'])
def delBook(book_id=None):
    if request.method == 'GET':
        del_book = Basket.query.filter(Basket.book_id == book_id and Basket.client_login == request.cookies.get('client_login')).first()
        db.session.delete(del_book)
        db.session.commit()
        return redirect(url_for("basket"))


@app.route("/get_order", methods=['GET', 'POST'])
def getOrder():
    if request.method == 'GET':
        price = 0
        books = Basket.query.filter(Basket.client_login == request.cookies.get('client_login')).all()
        if books:
            for book in books:
                targ = Book.query.get(book.book_id)
                if targ.number >= book.number:
                    price += targ.price * book.number
                    targ.number -= book.number
            order = OrderJournal(price, request.cookies.get('client_login'))
            db.session.add(order)
            db.session.commit()
            for book in books:
                ord_str = Orders(order.order_id, book.book_id, book.number)
                db.session.add(ord_str)
                db.session.delete(book)
                db.session.commit()
            return redirect(url_for("orderJournal"))
        return redirect(url_for("basket"))


@app.route("/get_add", methods=['GET', 'POST'])
def getAdd():
    st = False
    if auth.isLoggedUser(request.cookies):
        st = True
        client = Client.query.get(request.cookies.get('client_login'))
    return render_template("add.html", auth=st, client=client, css_url=url_for('static', filename='css/style.css'))


@app.route("/add", methods=['GET', 'POST'])
def add():
    st = False
    if auth.isLoggedUser(request.cookies):
        st = True
        client = Client.query.get(request.cookies.get('client_login'))
    if request.method == 'GET':
        return render_template("add.html", auth=st, client=client, css_url=url_for('static', filename='css/style.css'))
    if request.method == 'POST':
        if request.form.get('name') and request.form.get('author') and request.args.get('price') and request.args.get('number'):
            book = Book(name=request.form.get('name'), author=request.form.get('author'), style=request.form.get('style'), price=request.form.get('price'), number=request.form.get('number'))
            db.session.add(book)
            db.session.commit()
            return redirect(url_for("hello"))
        else:
            return render_template('add.html', error="Заполните все поля!", auth=st, client=client, css_url=url_for('static', filename='css/style.css'))


@app.route("/delete/<book_id>", methods=['GET', 'POST'])
def delete(book_id=None):
    if request.method == 'GET':
        book = Book.query.get(book_id)
        db_data = OrderJournal.query.filter(OrderJournal.order_id == Orders.order_id).filter(Orders.book_id == book.book_id).all()
        for data in db_data:
           db.session.delete(data)
           db.session.commit()
        db_data = Orders.query.filter(Orders.book_id == book.book_id).all()
        for data in db_data:
           db.session.delete(data)
           db.session.commit()
        db_data = Basket.query.filter(Basket.book_id == book.book_id).all()
        for data in db_data:
           db.session.delete(data)
           db.session.commit()
        db.session.delete(book)
        db.session.commit()
        return redirect(url_for("hello"))


@app.route("/order_journal", methods=['GET', 'POST'])
def orderJournal():
    if request.method == 'GET':
        st = False
        if auth.isLoggedUser(request.cookies):
            st = True
            client = Client.query.get(request.cookies.get('client_login'))
            if client.isadmin:
                db_data = OrderJournal.query.filter(or_(OrderJournal.admin_login == client.client_login, OrderJournal.status == "принят"))
            else:
                db_data = OrderJournal.query.filter(OrderJournal.client_login == client.client_login)
        return render_template('orders.html', db_data=db_data, auth=st, client=client, css_url=url_for('static', filename='css/style.css'))


@app.route("/take_order/<order_id>", methods=['GET', 'POST'])
def takeOrder(order_id=None):
    if request.method == 'GET':
        order = OrderJournal.query.get(order_id)
        if order.status == "принят":
            order.admin_login = request.cookies.get('client_login')
            order.status = "в обработке"
        elif order.status == "в обработке":
            order.status = "собирается"
        elif order.status == "собирается":
            order.status = "готов"
        db.session.commit()
        return redirect(url_for("orderJournal"))


@app.route("/logout")
def logout():
    resp = make_response(redirect(url_for('login')))
    resp.set_cookie('userID', '', expires=0)
    resp.set_cookie('userLogin', '', expires=0)
    return resp


app.run(debug=True)
