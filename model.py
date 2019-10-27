from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Book(db.Model):
    book_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(50), nullable=False)
    style = db.Column(db.String(20))
    price = db.Column(db.Integer, nullable=False)
    number = db.Column(db.Integer, nullable=False)

    def __init__(self, name, author, style, price, number):
        self.name = name
        self.author = author
        self.style = style
        self.price = price
        self.number = number


class Client(db.Model):
    client_login = db.Column(db.String(15), primary_key=True)
    password = db.Column(db.String(15), nullable=False)
    fio = db.Column(db.String(50), nullable=False)
    address = db.Column(db.String(100), nullable=False)
    isadmin = db.Column(db.Boolean, nullable=False)

    def __init__(self, client_login, password, fio, address):
        self.client_login = client_login
        self.password = password
        self.fio = fio
        self.address = address
        self.isadmin = False


class OrderJournal(db.Model):
    order_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    cost = db.Column(db.Integer, nullable=False)
    admin_login = db.Column(db.String(15), db.ForeignKey("client.client_login"), nullable=True)
    client_login = db.Column(db.Integer, db.ForeignKey("client.client_login"), nullable=False)
    status = db.Column(db.String(10), nullable=False)

    def __init__(self, cost, client_login):
        self.cost = cost
        self.client_login = client_login
        self.status = "принят"


class Orders(db.Model):
    order_id = db.Column(db.Integer, db.ForeignKey("order_journal.order_id"), primary_key=True, nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey("book.book_id"), primary_key=True, nullable=False)
    number = db.Column(db.Integer, nullable=False)

    def __init__(self, order_id, book_id, number):
        self.order_id = order_id
        self.book_id = book_id
        self.number = number


class Basket(db.Model):
    client_login = db.Column(db.String(15), db.ForeignKey("client.client_login"), primary_key=True, nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey("book.book_id"), primary_key=True, nullable=False)
    number = db.Column(db.Integer, nullable=False)

    def __init__(self,client_login, book_id, number):
        self.client_login = client_login
        self.book_id = book_id
        self.number = number
