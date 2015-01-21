from flask import Flask, flash
from flask import session, redirect, render_template

from flask.ext.socketio import SocketIO, emit, join_room, leave_room

app = Flask(__name__)
app.debug = True

socketio = SocketIO(app)
room="test"
app.config['SECRET_KEY'] = ':3'

ctr = 0
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
        if (name['name'] in cursors.keys()):
            emit('msg', {'online' : ctr}, room=room)
        else:
            session['name'] = name['name']
            cursors[name['name']] = [0,0]
            ctr += 1
            emit('msg', {'message' : name['name'] + " has joined!", 'online' : ctr}, room=room)
            emit('join')
            emit('draw_all', {'players' : cursors}, room=room)
    #else user can only see how many are on chat
    else:
        emit('msg', {'online' : ctr}, room=room)

#disconnect is slow; according to documentation takes a few seconds to register 
@socketio.on('disconnect')
def leave():
#registers as a user leaving if user has 'logged into' chat
    if 'name' in session:
        emit('remove', {'user' : session['name']})
        leave_room(room)
        global ctr
        ctr -= 1
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
def mouse_move(coor):
    if 'name' in session:
        cursors[session['name']] = [coor['top'], coor['left']]
        emit('move_clientmouse' , {'x' : cursors[session['name']][0], 'y' : cursors[session['name']][1], 'user' : session['name']})

if __name__ == '__main__':
    socketio.run(app)
