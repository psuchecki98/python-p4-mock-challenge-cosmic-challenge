#!/usr/bin/env python3

from models import db, Scientist, Mission, Planet
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

class Scientists(Resource):

    def get(self):

        scientists = Scientist.query.all()

        scientists_dict = [scientist.to_dict(rules = ('-missions', )) for scientist in scientists]

        response = make_response(
            jsonify(scientists_dict),
            200
        )

        return response
    
    def post(self):

        data = request.get_json()

        try:

            new_scientist = Scientist(
                name = data['name'],
                field_of_study = data['field_of_study']
            )

            db.session.add(new_scientist)
            
            db.session.commit()

            response = make_response(
                jsonify(new_scientist.to_dict(rules = ('-missions', ))),
                201
            )

        except ValueError:

            response = make_response(
                { "errors": ["validation errors"] },
                400
            )

        return response
    
api.add_resource(Scientists, '/scientists')

@app.route('/scientists/<int:id>', methods = ['GET', 'PATCH', 'DELETE'])
def scientist_by_id(id):

    scientist = Scientist.query.filter(Scientist.id == id).first()

    if scientist:

        if request.method == 'GET':

            scientist_dict = scientist.to_dict()

            response = make_response(
                jsonify(scientist_dict),
                200
            )

        elif request.method == 'PATCH':

            data = request.get_json()

            try:

                for key in data:
                    setattr(scientist, key, data[key])

                db.session.add(scientist)

                db.session.commit()

                response = make_response(
                    jsonify(scientist.to_dict(rules = ('-missions', ))),
                    202
                )

            except ValueError:

                response = make_response(
                    { "errors": ["validation errors"] },
                    400
                )

        elif request.method == 'DELETE':

            missions = Mission.query.filter(Mission.scientist_id == id).all()

            for mission in missions:

                db.session.delete(mission)

            db.session.delete(scientist)

            db.session.commit()

            response = make_response(
                {},
                204
            )

    else:

        response = make_response(
            { "error": "Scientist not found" },
            404
        )

    return response

@app.route('/planets', methods = ['GET'])
def planets():

    planets = Planet.query.all()

    planets_dict = [planet.to_dict(rules = ('-missions', )) for planet in planets]

    # planets_dict = []

    # for planet in planets:

    #     planets_dict.append(planet.to_dict(rules = ('-missions', )))

    response = make_response(
        jsonify(planets_dict),
        200
    )

    return response

@app.route('/missions', methods = ['POST'])
def missions():

    data = request.get_json()

    try:

        new_mission = Mission(
            name = data['name'],
            scientist_id = data['scientist_id'],
            planet_id = data['planet_id']
        )

        db.session.add(new_mission)

        db.session.commit()

        response = make_response(
            jsonify(new_mission.to_dict()),
            201
        )

    except ValueError:

        response = make_response(
            { "errors": ["validation errors"] },
            400
        )

    return response


if __name__ == '__main__':
    app.run(port=5555, debug=True)