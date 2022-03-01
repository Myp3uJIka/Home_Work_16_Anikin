from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
import json
import datetime


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
app.config['JSON_AS_ASCII'] = False
app.config['JSON_SORT_KEYS'] = False
db = SQLAlchemy(app)


# создаём таблицы с помощью SQLAlchemy
class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String)
    last_name = db.Column(db.String)
    age = db.Column(db.Integer)
    email = db.Column(db.String)
    role = db.Column(db.String)
    phone = db.Column(db.String)

    # функция для упрощения вывода информации о конкретном пользователе
    def info(self):
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'age': self.age,
            'email': self.email,
            'role': self.role,
            'phone': self.phone,
        }


class Order(db.Model):
    __tablename__ = 'order'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    description = db.Column(db.String)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    address = db.Column(db.String)
    price = db.Column(db.Integer)
    customer_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))
    executor_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def info(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'address': self.address,
            'price': self.price,
            'customer_id': self.customer_id,
            'executor_id': self.executor_id,
        }


class Offer(db.Model):
    __tablename__ = 'offer'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'))
    executor_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def info(self):
        return {
            'id': self.id,
            'order_id': self.order_id,
            'executor_id': self.executor_id,
        }


db.create_all()

# добавляем данные в таблицы из файла "data.json"
with open('data.json', 'r', encoding='utf-8') as f:
    data = json.loads(f.read())
    for u in data['users']:
        user = User(
            id=u['id'],
            first_name=u['first_name'],
            last_name=u['last_name'],
            age=u['age'],
            email=u['email'],
            role=u['role'],
            phone=u['phone']
        )
        db.session.add(user)
    for o in data['orders']:
        order = Order(
            id=o['id'],
            name=o['name'],
            description=o['description'],
            start_date=datetime.datetime.strptime(o['start_date'], '%m/%d/%Y'),
            end_date=datetime.datetime.strptime(o['end_date'], '%m/%d/%Y'),
            address=o['address'],
            price=o['price'],
            customer_id=o['customer_id'],
            executor_id=o['executor_id']
        )
        db.session.add(order)
    for of in data['offers']:
        offer = Offer(
            id=of['id'],
            order_id=of['order_id'],
            executor_id=of['executor_id']
        )
        db.session.add(offer)
    db.session.commit()
    db.session.close()


@app.route('/users', methods=['GET', 'POST'])
def show_users():
    """
    Отображает список пользователей и добавляет новых пользователей.
    GET - выводит список пользователей занесённых в БД.
    POST - обрабатывает запрос создания нового пользователя. Для проверки можно использовать, например, созданную
    html-форму "check_page.html"
    :return: GET - список пользователей,
            POST - сообщение о выполнении.
    """
    users = db.session.query(User).all()
    result = []
    if request.method == 'GET':
        for user in users:
            result.append(user.info())
        return jsonify(result)
    elif request.method == 'POST':
        user_id = int(request.form.get('id'))
        while db.session.query(User).get(user_id):
            user_id += 1
        new_user = User(
            id=user_id,
            first_name=request.form.get('first_name'),
            last_name=request.form.get('last_name'),
            age=request.form.get('age'),
            email=request.form.get('email'),
            role=request.form.get('role'),
            phone=request.form.get('phone'),
        )
        db.session.add(new_user)
        db.session.commit()
        db.session.close()
        return 'Done'


@app.route('/users/<idx>', methods=['GET', 'PUT', 'DELETE'])
def current_user(idx):
    # TODO шаг6 - В Body будет приходить JSON со всеми полями для обновление заказа. Что это означает?
    """
    Отображает, изменяет и удаляет информацию о конкретном пользователе.
    'GET' запрос выводит данные о конкретном пользователе по указанному id (idx)
    Проверка метода "PUT", например, выполняется с помощью httpie. Запрос выглядит следующим образом (пример):
    -----
    http Put "http://127.0.0.1:5000/users/1" first_name=Joseph, last_name=Biden, age=79
    -----
    Проверка метода "DELETE", например, выполняется с помощью httpie. Запрос выглядит следующим образом (пример):
    -----
    http Delete "http://127.0.0.1:5000/users/10"
    -----
    :param idx: id пользователя
    :return: для GET - данные об указанном пользователе,
            для PUT - сообщение об успешном обновлении данных пользователя,
            для DELETE - сообщение с указанием идентификатора удалённого пользователя.
    """
    if request.method == 'GET':
        return jsonify(db.session.query(User).get(idx).info())
    elif request.method == 'PUT':
        updated_data = json.loads(request.data)
        user = User.query.get(idx)
        try:
            user.first_name = updated_data["first_name"]
        except:
            pass
        try:
            user.last_name = updated_data["last_name"]
        except:
            pass
        try:
            user.age = updated_data["age"]
        except:
            pass
        try:
            user.email = updated_data["email"]
        except:
            pass
        try:
            user.role = updated_data["role"]
        except:
            pass
        try:
            user.phone = updated_data["phone"]
        except:
            pass
        db.session.commit()
        db.session.close()
        return f"Updated user {idx} success"
    elif request.method == 'DELETE':
        user = User.query.get(idx)
        db.session.delete(user)
        db.session.commit()
        db.session.close()
        return f'Deleted: {idx}'


@app.route('/orders', methods=['GET', 'POST'])
def show_orders():
    #TODO странно, что поле даты должно быть определённого формата, а вот цена или customer_id может быть как цифрой,
    # так и текстом, хотя у поля тип Integer
    """
    Отображает список заказов и добавляет новые.
    GET - выводит список заказов занесённых в БД.
    POST - обрабатывает запрос создания нового заказа. Для проверки можно использовать, например, созданную
    html-форму "check_page.html"
    :return: GET - список заказов,
            POST - сообщение о выполнении.
    """
    orders = db.session.query(Order).all()
    result = []
    if request.method == 'GET':
        for order in orders:
            result.append(order.info())
        return jsonify(result)
    elif request.method == 'POST':
        order_id = int(request.form.get('id'))
        while db.session.query(Order).get(order_id):
            order_id += 1
        new_order = Order(
            id=order_id,
            name=request.form.get('name'),
            description=request.form.get('description'),
            start_date=datetime.datetime.strptime(request.form.get('start_date'), '%m/%d/%Y'),
            end_date=datetime.datetime.strptime(request.form.get('end_date'), '%m/%d/%Y'),
            address=request.form.get('address'),
            price=request.form.get('price'),
            customer_id=request.form.get('customer_id'),
            executor_id=request.form.get('executor_id'),
        )
        db.session.add(new_order)
        db.session.commit()
        db.session.close()
        return 'Done'


@app.route('/orders/<idx>', methods=['GET', 'PUT', 'DELETE'])
def show_current_order(idx):
    """
    Отображает, изменяет и удаляет информацию о конкретном заказе.
    'GET' запрос выводит данные о конкретном заказе по указанному id (idx)
    Проверка метода "PUT" (дата вводится в формате: MM/DD/YYYY), например, выполняется с помощью httpie.
    Запрос выглядит следующим образом (пример):
    -----
    http Put "http://127.0.0.1:5000/orders/1" name=ДЗ_Alchemy, description=создание_БД_и_представлений_Flask
    -----
    Проверка метода "DELETE", например, выполняется с помощью httpie. Запрос выглядит следующим образом (пример):
    -----
    http Delete "http://127.0.0.1:5000/orders/10"
    -----
    :param idx: id заказа
    :return: для GET - данные об указанном заказе,
            для PUT - сообщение об успешном обновлении данных заказа,
            для DELETE - сообщение с указанием идентификатора удалённого заказа.
    """
    if request.method == 'GET':
        return jsonify(db.session.query(Order).get(idx).info())
    elif request.method == 'PUT':
        updated_data = json.loads(request.data)
        order = Order.query.get(idx)
        try:
            order.name = updated_data["name"]
        except:
            pass
        try:
            order.description = updated_data["description"]
        except:
            pass
        try:
            order.start_date = updated_data["start_date"]
        except:
            pass
        try:
            order.end_date = updated_data["end_date"]
        except:
            pass
        try:
            order.address = updated_data["address"]
        except:
            pass
        try:
            order.price = updated_data["price"]
        except:
            pass
        try:
            order.customer_id = updated_data["customer_id"]
        except:
            pass
        try:
            order.executor_id = updated_data["executor_id"]
        except:
            pass
        db.session.commit()
        db.session.close()
        return f"Updated order {idx} success"
    elif request.method == 'DELETE':
        order = Order.query.get(idx)
        db.session.delete(order)
        db.session.commit()
        db.session.close()
        return f'Deleted: {idx}'


@app.route('/offers', methods=['GET', 'POST'])
def show_offers():
    """
   Отображает список предложений и добавляет новые.
   GET - выводит список предложений занесённых в БД.
   POST - обрабатывает запрос создания нового предложения. Для проверки можно использовать, например, созданную
   html-форму "check_page.html"
   :return: GET - список предложений,
           POST - сообщение о выполнении.
   """
    offers = db.session.query(Offer).all()
    result = []
    if request.method == 'GET':
        for offer in offers:
            result.append(offer.info())
        return jsonify(result)
    elif request.method == 'POST':
        offer_id = int(request.form.get('id'))
        while db.session.query(Offer).get(offer_id):
            offer_id += 1
        new_offer = Offer(
            id=offer_id,
            order_id=request.form.get('order_id'),
            executor_id=request.form.get('executor_id'),
        )
        db.session.add(new_offer)
        db.session.commit()
        db.session.close()
        return 'Done'


@app.route('/offers/<idx>', methods=['GET', 'PUT', 'DELETE'])
def show_current_offer(idx):
    """
    Отображает, изменяет и удаляет информацию о конкретном предложении.
    'GET' запрос выводит данные о конкретном предложении по указанному id (idx)
    Проверка метода "PUT", например, выполняется с помощью httpie.
    Запрос выглядит следующим образом (пример):
    -----
    http Put "http://127.0.0.1:5000/offers/69" order_id=1, executor_id=2
    -----
    Проверка метода "DELETE", например, выполняется с помощью httpie. Запрос выглядит следующим образом (пример):
    -----
    http Delete "http://127.0.0.1:5000/offers/2"
    -----
    :param idx: id предложения
    :return: для GET - данные об указанном предложении,
            для PUT - сообщение об успешном обновлении данных предложения,
            для DELETE - сообщение с указанием идентификатора удалённого предложения.
    """
    if request.method == 'GET':
        return jsonify(db.session.query(Offer).get(idx).info())
    elif request.method == 'PUT':
        updated_data = json.loads(request.data)
        offer = Offer.query.get(idx)
        try:
            offer.order_id = updated_data["order_id"]
        except:
            pass
        try:
            offer.executor_id = updated_data["executor_id"]
        except:
            pass
        db.session.commit()
        db.session.close()
        return f"Updated offer {idx} success"
    elif request.method == 'DELETE':
        offer = Offer.query.get(idx)
        db.session.delete(offer)
        db.session.commit()
        db.session.close()
        return f'Deleted: {idx}'


if __name__ == "__main__":
    app.run(debug=True)
