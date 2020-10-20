from flask import Flask
from flask_classful import FlaskView, route

app = Flask(__name__)

class SpotifyAPI(FlaskView):

    def index(self):
    # http://localhost:5000/
        return "<h1>This is my indexpage</h1>"

    @route("/callback/q")
    def bsicname(self):
    # customized route
    # http://localhost:5000/diffrentname
        return "<h1>This is my coustom route</h1>"

SpotifyAPI.register(app,route_base = '/')

if __name__ == '__main__':
    app.run(debug=True)