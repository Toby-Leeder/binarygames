import json
from flask import Blueprint, request, jsonify
from flask_restful import Api, Resource # used for REST API building
from datetime import datetime

from model.gamers import Gamer
from model.gamers import getUser

gamer_api = Blueprint('gamer_api', __name__,
                   url_prefix='/api/gamers')

# API docs https://flask-restful.readthedocs.io/en/latest/api.html
api = Api(gamer_api)

class GamerAPI:        
    class _Create(Resource):
        def post(self):
            ''' Read data for json body '''
            body = request.get_json()
            
            ''' Avoid garbage in, error checking '''
            # validate name
            name = body.get('name')
            if name is None or len(name) < 2:
                return {'message': f'Name is missing, or is less than 2 characters'}, 400
            # look for password and dob
            password = body.get('password')

            ''' #1: Key code block, setup USER OBJECT '''
            uo = Gamer(name=name)
            
            ''' Additional garbage error checking '''
            # set password if provided
            if password is not None:
                uo.set_password(password)
            
            ''' #2: Key Code block to add user to database '''
            # create user in database
            user = uo.create()
            # success returns json of user
            if user:
                return jsonify(user.read())
            # failure returns error
            return {'message': f'Processed {name}, either a format error or is duplicate'}, 400

    class _Read(Resource):
        def get(self):
            users = Gamer.query.all()    # read/extract all users from database
            json_ready = [user.read() for user in users]  # prepare output in json
            return jsonify(json_ready)  # jsonify creates Flask response object, more specific to APIs than json.dumps
    
    class _Security(Resource):

        def post(self):
            ''' Read data for json body '''
            body = request.get_json()

            user = getUser(body.get("name"))

            password = body.get('password')

            if user is None:
                return {'message': f"invalid username"}, 400
            
            if not user.is_password(password):
                return {'message': f"wrong password"}, 400

            ''' authenticated user '''
            return jsonify(user.read())

            

    # building RESTapi endpoint
    api.add_resource(_Create, '/create')
    api.add_resource(_Read, '/')
    api.add_resource(_Security, '/authenticate')
    