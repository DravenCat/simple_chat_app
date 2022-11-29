from flask import Blueprint
from flask import jsonify, request
import json
import pymongo
import uuid

api = Blueprint('api', __name__)

online_user = []

client = pymongo.MongoClient("localhost", 27017)
mongo = client["chatApp"]
# test database connectivity
try:
    print(client.server_info())
except Exception:
    print("Unable to connect to mongodb")
'''
{
    username: String
    password: String
    session: List of session id
}
'''
users = mongo['user']

'''
{
    id: String
    members: List of username
    history: 
    List of {
        content: String
        sender: username
        time: datatime
    }
}
    '''
chat_sessions = mongo['chatSession']


@api.route("/account/login", methods=['POST'])
def login():
    req_body = request.json
    username = req_body['username']
    password = req_body['password']

    if username is None:
        return json.dumps({'message': "Missing username"}), 400
    elif password is None:
        return json.dumps({'message': "Missing password"}), 400
    elif username in online_user:
        return json.dumps({'message': "user already logged in"}), 400
    else:
        user = users.find_one({"username": username})
        if user is None:
            return json.dumps({'message': "User does not exist"}), 404
        elif user['password'] != password:
            return json.dumps({'message': "Password incorrect"}), 400
        else:
            online_user.append(user['username'])
            res = jsonify({
                'username': user['username'],
                'session': user['session']
            })
            return res, 200


@api.route("/account/register", methods=["POST"])
def register():
    req_body = request.json
    username = req_body['username']
    password = req_body['password']

    if username is None:
        return json.dumps({'message': "Missing username"}), 400
    elif password is None:
        return json.dumps({'message': "Missing password"}), 400
    elif username in online_user:
        return json.dumps({'message': "Username already exists"}), 400
    else:
        user = users.find_one({"username": username})
        if user:
            json.dumps({'message': "Username already exists"}), 400
        else:
            users.insert_one({'username': username, 'password': password, 'session': []})
            res = jsonify({
                'message': 'success'
            })
            return res, 200


@api.route("/account/logout", methods=["POST"])
def logout():
    req_body = request.json
    username = req_body['username']

    if username is None:
        return json.dumps({'message': "Missing username"}), 400
    elif username not in online_user:
        return json.dumps({'message': "Already logged out"}), 400
    else:
        online_user.remove(username)
        res = jsonify({
            'message': 'success'
        })
        return res, 200


@api.route("/session/join", methods=["POST"])
def join():
    req_body = request.json
    usernames = req_body['username']
    session = {
                'id': str(uuid.uuid4()),
                'members': [],
                'history': []
              }
    for username in usernames:
        user = users.find_one({'username': username})
        if user:
            session['members'].append(user['username'])
            user['session'].append(session['id'])
            users.update_one({'username': user['username']}, {'$set': {'session': user['session']}})

    chat_sessions.insert_one(session)
    res = jsonify({
        'message': 'success'
    })
    return res, 200


@api.route("/session", methods=["GET"])
def history():
    session_id = request.args.get('sessionId')
    session = chat_sessions.find_one({'id': session_id})
    if session is None:
        return json.dumps({'message': "Session does not exist"}), 400

    res = jsonify({
        'sessionId': session_id,
        'members': session['members'],
        'history': session['history']
    })
    return res, 200
