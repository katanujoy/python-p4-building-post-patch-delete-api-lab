from flask import Flask, request, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from models import db, Bakery, BakedGood

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)

@app.route('/')
def index():
    return '<h1>Bakery API</h1>'

@app.route('/bakeries')
def bakeries():
    bakeries = [bakery.to_dict() for bakery in Bakery.query.all()]
    return make_response(bakeries, 200)

@app.route('/bakeries/<int:id>', methods=['GET', 'PATCH'])
def bakery_by_id(id):
    bakery = Bakery.query.get(id)
    if not bakery:
        return make_response({'error': 'Bakery not found'}, 404)
    
    if request.method == 'PATCH':
        new_name = request.form.get('name')
        if not new_name:
            return make_response({'error': 'Name is required'}, 400)
        
        try:
            bakery.name = new_name
            db.session.commit()
            return make_response(bakery.to_dict(), 200)
        except Exception as e:
            db.session.rollback()
            return make_response({'error': str(e)}, 400)
    
    return make_response(bakery.to_dict(), 200)

@app.route('/baked_goods', methods=['POST'])
def create_baked_good():
    name = request.form.get('name')
    price = request.form.get('price')
    bakery_id = request.form.get('bakery_id')
    
    if not all([name, price, bakery_id]):
        return make_response({'error': 'Missing required fields (name, price, bakery_id)'}, 400)
    
    try:
        new_baked_good = BakedGood(
            name=name,
            price=float(price),
            bakery_id=int(bakery_id)
        )
        db.session.add(new_baked_good)
        db.session.commit()
        return make_response(new_baked_good.to_dict(), 201)
    except Exception as e:
        db.session.rollback()
        return make_response({'error': str(e)}, 400)

@app.route('/baked_goods/<int:id>', methods=['DELETE'])
def delete_baked_good(id):
    baked_good = BakedGood.query.get(id)
    if not baked_good:
        return make_response({'error': 'Baked good not found'}, 404)
    
    try:
        db.session.delete(baked_good)
        db.session.commit()
        return make_response({'message': 'Baked good successfully deleted'}, 200)
    except Exception as e:
        db.session.rollback()
        return make_response({'error': str(e)}, 400)

@app.route('/baked_goods/by_price')
def baked_goods_by_price():
    baked_goods = BakedGood.query.order_by(BakedGood.price.desc()).all()
    baked_goods_dict = [bg.to_dict() for bg in baked_goods]
    return make_response(baked_goods_dict, 200)

@app.route('/baked_goods/most_expensive')
def most_expensive_baked_good():
    baked_good = BakedGood.query.order_by(BakedGood.price.desc()).first()
    if not baked_good:
        return make_response({'error': 'No baked goods found'}, 404)
    return make_response(baked_good.to_dict(), 200)

if __name__ == '__main__':
    app.run(port=5555, debug=True)