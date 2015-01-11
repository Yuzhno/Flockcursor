from flask import Flask
from flask import session, redirect, render_template

from flask.ext.socketio import SocketIO, emit, join_room, leave_room

app = Flask(__name__)
app.debug = True

socketio = SocketIO(app)
room="test"
app.config['SECRET_KEY'] = ':3'

@app.route('/')
def interface():
    session['name'] = 'anon'
    return render_template('index.html')

@socketio.on('joined')
def joined(message):
    join_room(room)
    emit('msg', {'message' : "A user has joined!"}, room=room)

@socketio.on('user_msg')
def user_msg(message):
    name = session['name']
    emit('msg', {'message' : name + ': ' + message['message']}, room=room)

@socketio.on('change_name')
def change_name(new):
    old = session['name']
    session['name'] = new['new']
    emit('msg', {'message' : old + ' has changed their name to ' + new['new']}, room=room)

if __name__ == '__main__':
    socketio.run(app)
