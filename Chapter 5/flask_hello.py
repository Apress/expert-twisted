import flask 

application = flask.Flask(__name__)

@application.route("/")
def hello():
    return "Hello World!"
