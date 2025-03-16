#!/usr/bin/env python3

from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)


@app.route('/')
def index():
    return '<h1>Code challenge</h1>'


class Restaurants(Resource):
    def get(self):
        response_dict_list = [n.to_dict(rules=('-restaurant_pizzas',)) for n in Restaurant.query.all()]
        response = make_response(
            response_dict_list,
            200
        )
        return response
    
api.add_resource(Restaurants, '/restaurants')

class RestaurantByID(Resource):
    def get(self, id):
        restaurant = Restaurant.query.filter(Restaurant.id == id).first()
        if restaurant:
            response = make_response(
                restaurant.to_dict(),
                200
            )
            return response
        else:
            response_dict = {
                "error": "Restaurant not found"
            }
            response = make_response(
                response_dict,
                404
            )
            return response
        
    def delete(self, id):
        restaurant = Restaurant.query.filter(Restaurant.id == id).first()
        if restaurant:
            db.session.delete(restaurant)
            db.session.commit()
            response_dict = {
                "message": ""
            }
            response = make_response(
                response_dict,
                204
            )
            return response
        else:
            response_dict = {
                "error": "Restaurant not found"
            }
            response = make_response(
                response_dict,
                404
            )
            return response
    
api.add_resource(RestaurantByID, '/restaurants/<int:id>')


class Pizzas(Resource):
    def get(self):
        response_dict_list = [n.to_dict(rules=('-restaurants',)) for n in Pizza.query.all()]
        response = make_response(
            response_dict_list,
            200
        )
        return response
    
api.add_resource(Pizzas, '/pizzas')

class PizzaByID(Resource):
    def post(self):
        try:  
            data = request.get_json()  
            new_pizza = RestaurantPizza(  
                price=data['price'], 
                pizza_id=data['pizza_id'],    
                restaurant_id=data['restaurant_id'],
            )  
            db.session.add(new_pizza)  
            db.session.commit()  

            response = make_response(
                new_pizza.to_dict(),
                201
            )  
            return response  

        except Exception:  
            return make_response({"errors": ["validation errors"]}, 400) 
        

api.add_resource(PizzaByID, '/restaurant_pizzas')
        

if __name__ == '__main__':
    app.run(port=5555, debug=True)