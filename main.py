from flask import Flask, flash
from flask import session, redirect, render_template

from flask.ext.socketio import SocketIO, emit, join_room, leave_room

class cursor:
    def __init__(self, name):
        self.coord = [0, 0]
        self.name = name


app = Flask(__name__)
app.debug = True

socketio = SocketIO(app)
room="test"
app.config['SECRET_KEY'] = ':3'

ctr = 0
users = []
cursors = {}

@app.route('/')
def interface():
    return render_template('index.html', online=ctr)

#user connects to page. announces user joining in chat
@socketio.on('joined')
def joined(name):
    #joins if user submits a nickname
    join_room(room)
    global ctr
    if (name != {}):

        #no user repeats
        if (name['name'] in users):
            emit('msg', {'online' : ctr}, room=room)

        else:
            session['name'] = name['name']
            cursors['name'] = [0,0]
            ctr += 1
            users.append(name['name'])
            emit('msg', {'message' : name['name'] + " has joined!", 'online' : ctr}, room=room)
            emit('join')
    #else user can only see how many are on chat
    else:
        emit('msg', {'online' : ctr}, room=room)

#disconnect is slow; according to documentation takes a few seconds to register 
@socketio.on('disconnect')
def leave():
#registers as a user leaving if user has 'logged into' chat
    if ('name' in session):
        leave_room(room)
        global ctr
        ctr -= 1
        users.remove(session['name'])
        emit('msg', {'message' : session['name'] + " has left!", 'online' : ctr} , room=room)
        
#User chat-prompt. Sends message to js function -> prints message in chat
@socketio.on('user_msg')
def user_msg(message):
    name = session['name']
    emit('msg', {'message' : name + ': ' + message['message']}, room=room)

#User chat-name. Sets new name. Sends message regarding change to js function
@socketio.on('change_name')
def change_name(new):
    #if user has a name already
    if ('name' in session):

        #no user repeats
        if (new['new'] in users):
            emit('msg', {'online' : ctr}, room=room)
            
        else:
            old = session['name']
            users.remove(old)
            session['name'] = new['new']
            users.append(new['new'])
            emit('msg', {'message' : old + ' has changed their name to ' + new['new']}, room=room)

    #user has no name -> will get a name and have chat access
    else:
        joined( {'name' : new['new']} )

@socketio.on('mouse_move')
def mouse_move(x , y):
    cursors[session['name']] = [x , y]
    emit('move_clientmouse' , {'x' : x , 'y' : y , user : session['name']})
    

if __name__ == '__main__':
    socketio.run(app)
