#!/usr/bin/env python3

from models import db, Activity, Camper, Signup
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
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
def home():
    return ''

class Campers(Resource):

    # GET requests
    def get(self):
        campers = [camper.to_dict(rules=("-signups",)) for camper in Camper.query.all()]
        return make_response(campers, 200)
    
    # POST request (get_json instead of request.json ???)
    def post(self):
        try:
            new_camper = Camper(
                name = request.json['name'],
                age = request.json['age'])
            db.session.add(new_camper)
            db.session.commit()
        except ValueError:
            return make_response({ "errors": ["validation errors"] }, 400)

        return make_response(new_camper.to_dict(), 201)

    
class CampersById(Resource):
    
    def get(self, id):
        camper = Camper.query.filter(Camper.id == id).first()

        if camper:
            return make_response(camper.to_dict(), 200)
        
        return make_response({"error": "Camper not found"}, 404)
    
    # PATCH
    def patch(self, id):
        camper = Camper.query.filter(Camper.id == id).first()
        
        if camper:
            try:
                setattr(camper, 'name', request.json['name'])
                setattr(camper, 'age', request.json['age'])
                db.session.add(camper)
                db.session.commit()

                return make_response(camper.to_dict(rules=('-signups',)), 202)
            except ValueError:
                return make_response({"errors": ["validation errors"]}, 400)
        else:
            return make_response({"error": "Camper not found"}, 404)


class Activities(Resource):
    
    def get(self):
        activities = [activity.to_dict(rules=('-signups',)) for activity in Activity.query.all()]
        return make_response(activities, 200)

class ActivitiesById(Resource):
    def delete(self, id):
        activity = Activity.query.filter_by(id=id).first()
        if activity:
            db.session.delete(activity)
            db.session.commit()
            
            return make_response({}, 204)
        
        return make_response({"error": "Activity not found"}, 404)

class Signups(Resource):
    
    def post(self):
        try:
            signup = Signup(
                time = request.json['time'],
                camper_id = request.json['camper_id'],
                activity_id = request.json['activity_id'],
            )
            db.session.add(signup)
            db.session.commit()
            return make_response(signup.to_dict(), 201)
        
        except ValueError:
            return make_response({"errors": ["validation errors"]}, 400)

api.add_resource(Campers, "/campers")
api.add_resource(CampersById, "/campers/<int:id>")
api.add_resource(Activities, "/activities")
api.add_resource(ActivitiesById, "/activities/<int:id>")
api.add_resource(Signups, "/signups")

if __name__ == '__main__':
    app.run(port=5555, debug=True)
