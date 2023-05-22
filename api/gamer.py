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
            body = request.get_json()

            name = body.get('name')
            if not name or len(name) < 2:
                return {'message': 'Name is missing or less than 2 characters'}, 400

            password = body.get('pass')

            uo = Gamer(name=name)

            if password:
                uo.set_password(password)

            user = uo.create()

            if user:
                return jsonify(user.read())
            else:
                return {'message': f'Error creating user {name}'}, 400


    class _Read(Resource):
        def get(self):
            users = Gamer.query.all()    # read/extract all users from database
            json_ready = [user.read() for user in users]  # prepare output in json
            return jsonify(json_ready)  # jsonify creates Flask response object, more specific to APIs than json.dumps
    
    # class _Delete(Resource):
    #     def delete(self):
    #         body = request.get_json(force=True)

    #         name = body.get("name")

    #         password = body.get("pass")

    #         if(not name):
    #             return {'message': f"no name found"}, 400
            
    #         try:
    #             user = getUser(name)
    #             if not user:
    #                 return {'message': 'User not found'}, 400
    #         except ValueError:
    #             return {'message': 'User not found'}, 400
            
    #         if user.is_password(password):
    #             user.delete()
    #             return f"{user.read()} has been deleted", 200
    #         else:
    #             return {'message': f"Incorrect password"}, 400
            
    class _Delete(Resource):
        def delete(self):
            body = request.get_json(force=True)

            name = body.get("name")

            if(not name):
                return {'message': f"no name found"}, 400
            
            try:
                user = getUser(name)
                if not user:
                    return {'message': 'User not found'}, 400
                else:
                    user.delete()
            except ValueError:
                return {'message': 'User not found'}, 400
                
                
            
    class _Clear(Resource):
        def delete(self):
            table = Gamer.query.all()
            for user in table:
                user.delete()

            return {'message': f"Cleared the table"}, 200

        

    class _Update(Resource):
        def put(self):
            body = request.get_json()
            password = body.get('pass')
            data = body.get('data')
            name = body.get('name')

            try:
                user = getUser(name)
                if not user:
                    return {'message': 'User not found'}, 400
            except ValueError:
                return {'message': 'User not found'}, 400

            if user.is_password(password):
                user.update(data)
                return f"{user.read()} has been updated", 200
            else:
                return {'message': 'Incorrect password'}, 400




    class _Security(Resource):

        def post(self):
            ''' Read data for json body '''
            body = request.get_json()

            user = getUser(body.get("name"))

            password = body.get('password')

            if user is None:
                return {'message': "invalid username"}, 400
            
            if not user.is_password(password):
                return {'message': "incorrect password"}, 400

            ''' authenticated user '''
            return jsonify(user.read())

            

    # building RESTapi endpoint
    api.add_resource(_Create, '/create')
    api.add_resource(_Delete, '/delete')
    api.add_resource(_Update, '/update')
    api.add_resource(_Clear, '/clear')
    api.add_resource(_Read, '/')
    api.add_resource(_Security, '/authenticate')
    