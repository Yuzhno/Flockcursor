from flask import Flask , render_template , request
from flask.ext.socketio import SocketIO

app = Flask(__name__)
socketio = SocketIO(app)

@app.route("/")
def home():
    return render_template("home.html")

if __name__ == "__main__":
    app.debug = True
    app.run()
    #socketio.run(app)
