from flask import Flask
import config

app = Flask(__name__)


@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'


if __name__ == '__main__':
    app.config.from_object(config)
    app.run()
