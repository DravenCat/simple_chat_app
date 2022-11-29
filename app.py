from flask import Flask
from routes.account import account

app = Flask(__name__)
app.register_blueprint(account)


@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000, debug=False)
