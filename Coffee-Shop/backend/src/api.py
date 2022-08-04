import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink, db
from werkzeug.http import HTTP_STATUS_CODES
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
# db_drop_and_create_all()

# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks', methods=['GET'])
def get_all_drink():
    data = Drink.query.all()
    return jsonify({
        'success': True,
        'drinks': [drink.short() for drink in data],
        'total': len(data)
    }), 200


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def drinks_details(jwt):
    data = Drink.query.all()
    drinks = [drink.long() for drink in data]
    return jsonify({
        'success':True,
        'drinks': drinks,
    }), 200

'''

#Manager token
# eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IjFGNEJqM0tBZ2VLQm5BMUNFTFMtRiJ9.eyJpc3MiOiJodHRwczovL2FseGJhY2tlbmQudXMuYXV0aDAuY29tLyIsInN1YiI6ImF1dGgwfDYyY2VhNjA1M2JkY2YxMWZmNWRjMTU5NSIsImF1ZCI6ImNvZmZlZSIsImlhdCI6MTY1NzcxMDA5NywiZXhwIjoxNjU3NzE3Mjk3LCJhenAiOiJIQ0hGUEhLNzV3NUVwWEE1SFBJY0d0ejdneVl0eEF0WCIsInNjb3BlIjoiIiwicGVybWlzc2lvbnMiOltdfQ.0MoX0nWxkctE6gmrnD3hboFxoyN4hWhMPAtp6Qa966lnX12fm73eH_KuwH-Lrvu3e21nRitkcOiiZ4mwFBRi6pFVVu7aNMDAQxAveJuWMbFCKsm0UvdteJITaBpuTO-WT4jyLiDVnWFpberWTeNB1LNne1o5aoWVwZ1hfZFAnjrsfDROQWUDkmoA81TFL2Pt3awfBk0vQFufFQK-xSljwNfEtG80BEHZhs171OkXGLGVArYJ9Kd-lvSq3sR2cgzf3B8Y29L5mUkeJmfXYxTQsjxYc8qSvdiB1-t9Z9-nNtTj2KbHmaC_WE26Ojf9GDO2Yk5fUdFFdhKUuPLI0n737w

#Barister token
# eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IjFGNEJqM0tBZ2VLQm5BMUNFTFMtRiJ9.eyJpc3MiOiJodHRwczovL2FseGJhY2tlbmQudXMuYXV0aDAuY29tLyIsInN1YiI6ImF1dGgwfDYyYmRiYTM0M2MxMDNmYWM4YzFjMjUzZiIsImF1ZCI6ImNvZmZlZSIsImlhdCI6MTY1NzcwNjA2NiwiZXhwIjoxNjU3NzEzMjY2LCJhenAiOiJIQ0hGUEhLNzV3NUVwWEE1SFBJY0d0ejdneVl0eEF0WCIsInNjb3BlIjoiIiwicGVybWlzc2lvbnMiOlsiZ2V0OmRyaW5rcyIsImdldDpkcmlua3MtZGV0YWlsIl19.rfyC3WKJuJyjc6H_JNZFI1LHziSZECKCIXKW2KW-ldz_qCHQdvOjPzOV3ddPZlj7noxAs8Acjq0bpoOA9cYht_xT0EKz_kh-tX-KV5LuyLNiU8_-PSo3EiwffJDvK8N-KBVGKbunzZDKfRzmw-i717I8DrH5PUdGgC6LmlbtTwK1uuZGHor-cwmbuo-hCvII-tf1QZ9klWASQPu6qnP_-LPZ7So1hqtOzTPrjfqhiyelO_R3ACgcqZzkEsPII6urBGa0WELzshbFrT6LtYUomId9Jlh-pJxOjYVUv2825gMRtkZHb44rxZUaufDI8EsyHLjUXU6qvE4VVWacGtLH-g

@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def  add_drinks(jwt):
    data = request.get_json()
    title = data.get('title', None)
    recipe = data.get('recipe', None)
    print(data)
    try:
        drink = Drink(title = title, recipe = json.dumps(recipe))
        drink.insert()
        drinks = Drink.query.all()
        return jsonify({
            'success': True,
            'drinks': [ drink.long() for drink in drinks ]
        }), 200
    except:
        abort(404)

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
@requires_auth('patch:drinks')
def editDrinks(jwt, drink_id):
    jsonData = request.get_json()
    try:
        drink = Drink.query.filter(Drink.id == drink_id).first() 
        if drink is None:
            abort(404)

        if 'title' in jsonData and 'recipe' in jsonData:
            drink.title = jsonData.get('title')
            drink.recipe = json.dumps(jsonData.get('recipe'))
            drink.update()
        updated = Drink.query.all()
        return jsonify({
            'success':True,
            'drinks': [drink.long() for drink in updated]
        }), 200
    except:
        abort(404)

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
@requires_auth('delete:drinks')
def deleteDrinks(jwt, drink_id):
    try:
        drinks = Drink.query.filter(Drink.id == drink_id).first()
        if not drinks.id:
            abort(404)
        else:
            drinks.delete()
            return jsonify({
                'success':True,
                'delete': drink_id
            }), 200
    except:
        db.session.rollback()
        abort(442)
    

# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''
@app.errorhandler(405)
def not_allowed(error):
    return jsonify({
        'success':False,
        'error': 405,
        'message': 'method not allowed'
    }), 405

@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        'success':False,
        'error': 400,
        'message': 'Bad Request'
    }), 400
    
'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "Resource  not found"
    }), 404


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''
@app.errorhandler(AuthError)
def handle_error(err):
    return jsonify( {
        "message": HTTP_STATUS_CODES.get(err.status_code),
        "description": err.error,
    }), err.status_code