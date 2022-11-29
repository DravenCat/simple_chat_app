from flask import Flask
from routes.account import account
import pymongo

online_user = []

app = Flask(__name__)
app.register_blueprint(account)
client = pymongo.MongoClient("localhost", 27017)
mongo = client["chatApp"]
# test database connectivity
try:
    print(client.server_info())
except Exception:
    print("Unable to connect to mongodb")

user = mongo['user']
'''
{
    id: String
    username: String
    password: String
    friendList: String of user id
    session: List of session id
}
'''

chat_session = mongo['chatSession']
'''
{
    id: String
    members: List of user id
    history: 
    List of {
        content: String
        sender: user id
        time: datatime
    }
    
}
'''


@app.route('/')
def hello_world():
    return 'Hello World!'


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000, debug=False)
