import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
from flask_sqlalchemy import SQLAlchemy
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth


app = Flask(__name__, instance_relative_config=True)
setup_db(app)
CORS(app)

# cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
db_drop_and_create_all()

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PATCH,POST,DELETE,OPTIONS')
    return response


# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks}
    where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
# Get Endpoint for receiving short infos about the drinks

@app.route('/drinks', methods=['GET'])
@cross_origin()
def get_drinks():
    try:
        drinks_selection = Drink.query.all()
        drinks = [drink.short() for drink in drinks_selection]

        return jsonify({
            'success': True,
            'drinks': drinks
        }), 200
    except:
        abort(400)

'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
# Get Endpoint for receiving long infos about the drinks (details)
@app.route('/drinks-detail', methods=['GET'])
@cross_origin()
@requires_auth('get:drinks-detail')
def get_drinks_details():
    try:
        drinks_selection = Drink.query.order_by(Drink.id).all()
        drinks = [drink.long() for drink in drinks_selection]

        return jsonify({
            'success': True,
            'drinks': drinks
        }), 200
    except:
        abort(400)

'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
# Post Endpoint for creating a new drink
@app.route('/drinks', methods=['POST'])
@cross_origin()
@requires_auth('post:drinks')
def post_drink():
    body = request.get_json()
    titel = body['titel']
    recipe = body['recipe']

    # if there is no title or recipe -> abort
    if titel is None:
        abort(422)

    if recipe is None:
        abort(422)

    try:

        new_drink = Drink(titel=titel, recipe=recipe)

        new_drink.insert()

        return jsonify({
            'success': True,
            'drinks': [new_drink.long()]
        }), 200

    except Exception as e:
        print(e)
        abort(422)


'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@cross_origin()
@requires_auth('patch:drinks')
def patch_drinks(paylod, drink_id):
    body = request.get_json()
    titel = body['titel']
    recipe = body['recipe']

    if drink_id is None:
        abort(404)

    try:
        selected_drink = Drink.query.filter_by(id=drink_id).one_or_none()
        # if there is no title or recipe -> abort, else update the information
        if titel is None:
            abort(400)

        if recipe is None:
            abort(400)

        selected_drink.title = titel
        selected_drink.recipe = json.dumps(recipe)
        
        selected_drink.update()
        
        return jsonify({
            'success': True,
            'drinks': [selected_drink.long()]
        }), 200

    except Exception as e:
        print(e)
        abort(422)


'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@cross_origin()
@requires_auth('delete:drinks')
def delete_drink(payload, drink_id):
    body = request.get_json()

    # if there is no title or recipe -> abort
    if body is None:
        abort(422)

    try:
        
        if drink_id is None:
            abort(404)
        
        delete_drink = Drink.query.filter_by(id=drink_id).one_or_none()

        delete_drink.delete()


        return jsonify({
            'success': True,
            'delete': drink_id
        }), 200

    except Exception as e:
        print(e)
        abort(422)

## Error Handling
'''
Example error handling for unprocessable entity
'''
'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False, 
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''
'''
@TODO implement error handler for 404
    error handler should conform to general task above 
'''
# Implemented error handlers for 400, 404, 422, 500
@app.errorhandler(400)
def bad_request(error):
    return jsonify({
                    "success": False,
                    "error": 400,
                    "message": "bad request"
                    }), 400

@app.errorhandler(404)
def not_found(error):
    return jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
                    "success": False, 
                    "error": 422,
                    "message": "unprocessable"
                    }), 422

@app.errorhandler(500)
def server_error(error):
    return jsonify({
                    "success": False,
                    "error": 500,
                    "message": "internal server error"
                    }), 500

'''
@TODO implement error handler for AuthError
    error handler should conform to general task above 
'''

@app.errorhandler(AuthError)
def handle_auth_error(ex):
    """
    Receive the raised authorization error and propagates it as response
    """
    response = jsonify(ex.error)
    response.status_code = ex.status_code
    return response