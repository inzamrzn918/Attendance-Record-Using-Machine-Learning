from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import os

# Init app

app = Flask(__name__)
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, 'db.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATION'] = False

# INIT DB
db = SQLAlchemy(app)
# ma
ma = Marshmallow(app)


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    description = db.Column(db.String(200))
    price = db.Column(db.Float)
    qnt = db.Column(db.Integer)

    def __init__(self, name, description, price, qnt):
        self.name = name
        self.description = description
        self.price = price
        self.qnt = qnt


class ProductSchema(ma.Schema):
    class Meta:
        fields = ['id', 'name', 'description', 'price', 'qnt']


product_schema = ProductSchema()
products_schema = ProductSchema(many=True)


@app.route('/', methods=['GET'])
def index():
    all_products = Product.query.all()
    result = products_schema.dump(all_products)
    return jsonify(result)


@app.route('/<id>', methods=['GET'])
def index_one(id):
    product = Product.query.get(id)
    return product_schema.jsonify(product)


@app.route('/new_student', methods=['POST'])
def new_student():
    name = request.json['name']
    description = request.json['description']
    price = request.json['price']
    qnt = request.json['qnt']
    new_product = Product(name, description, price, qnt)
    db.session.add(new_product)
    db.session.commit()
    return product_schema.jsonify(new_product)


@app.route('/<id>', methods=['PUT'])
def update_student(id):
    product = Product.query.get(id)

    name = request.json['name']
    description = request.json['description']
    price = request.json['price']
    qnt = request.json['qnt']

    product.name = name
    product.description = description
    product.price = price
    product.qnt = qnt
    db.session.commit()
    return product_schema.jsonify(product)


# DELETE
@app.route('/<id>', methods=['DELETE'])
def index_delete(id):
    product = Product.query.get(id)
    db.session.delete(product)
    db.session.commit()
    return product_schema.jsonify(product)


# Run Server
if __name__ == '__main__':
    app.run(debug=True, port=5002)
