from flask import Flask, flash
from flask import session, redirect, render_template

from flask.ext.socketio import SocketIO, emit, join_room, leave_room

import re
from image_search import get_random_url, get_google_search

app = Flask(__name__)
app.debug = True

socketio = SocketIO(app)
room="test"
app.config['SECRET_KEY'] = ':3'

ctr = 0
cursors = {}
images = {}
screenshots = {}

clear = 0

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
            emit('diffname', {'name':name['name']})
        else:
            session['name'] = name['name']
            cursors[name['name']] = [0,0]
            ctr += 1
            emit('msg', {'message' : name['name'] + " has joined!", 'online' : ctr}, room=room)
            emit('join')
            emit('draw_all', {'players' : cursors}, room=room)
            emit('render_all', {'images' : images}, room=room)
    #else user can only see how many are on chat
    else:
        emit('msg', {'online' : ctr}, room=room)
    
#disconnect is slow; according to documentation takes a few seconds to register 
@socketio.on('disconnect')
def leave():
#registers as a user leaving if user has 'logged into' chat
    if 'name' in session:
        emit('remove', {'user' : session['name']}, room=room)
        del(cursors[session['name']])
        global ctr
        ctr -= 1
        emit('msg', {'message' : session['name'] + " has left!", 'online' : ctr} , room=room)
        leave_room(room)
        
#User chat-prompt. Sends message to js function -> prints message in chat
@socketio.on('user_msg')
def user_msg(message):
    reg_summon = re.search('(?<=^!summon )[\w ]+', message['message'])
    reg_del = re.search('^!delete', message['message'])
    reg_clr = re.search('^!clear', message['message'])
    name = session['name']
    if (reg_summon != None):
        fix = reg_summon.group(0).replace(" ", "%20")
        got_url = get_random_url(get_google_search(fix))
        if (got_url == None):
            emit('msg', {'message' : name + ' tried to summon a ' + reg_summon.group(0) + ' but failed!'}, room=room)
            return 1
        images[got_url] = [[0.4, 0.4], [10, 10], 0]
        emit('render_image', {'url' : got_url, 'message' : message}, room=room)
        emit('msg', {'message' : name + ' is summoning a ' + reg_summon.group(0) + '!'}, room=room)
    elif (reg_del != None and u'img_url' in message.keys()):
        del(images[message['img_url']])
        emit('delete_image', {'url' : message['img_url']}, room=room)
        emit('msg', {'message' : name + ' has deleted ' + message['img_url'] + '!'}, room=room)
    elif (reg_clr != None):
        global clear
        global ctr
        clear += 1
        if (clear >= (0.5 * ctr)):
            global images
            emit('clear_all', {}, room=room)
            images = {}
            emit('msg', {'message' : 'Canvas cleared!'}, room=room)
            clear = 0
        else:
            emit('msg', {'message' : name + ' wants to clear the canvas. Type !clear to agree. ' + str(0.5 * ctr) + ' people needed.'}, room=room)
    else:
        emit('msg', {'message' : name + ': ' + message['message']}, room=room)

#User chat-name. Sets new name. Sends message regarding change to js function
@socketio.on('change_name')
def change_name(new):
    #if name > 10 char
    if (len(new['new']) > 10):
        emit('diffname', {'name':new['new']})
    #if user has a name already
    elif ('name' in session):
        #no user repeats
        if (new['new'] in cursors.keys()):
            emit('msg', {'online' : ctr}, room=room)
            emit('diffname', {'name':new['new']})            
        else:
            old = session['name']
            coord = cursors[old]
            del cursors[old]
            session['name'] = new['new']
            cursors[session['name']] = coord
            emit('remove', {'user' : old }, room=room)
            emit('draw_one', {'user' : new['new'], 'coord' : coord }, room=room)
            emit('msg', {'message' : old + ' has changed their name to ' + new['new']}, room=room)

    #user has no name -> will get a name and have chat access
    else:
        joined( {'name' : new['new']} )

@socketio.on('mouse_move')
def mouse_move(coor):
    if 'name' in session:
        cursors[session['name']] = [coor['top'], coor['left']]
        emit('move_clientmouse' , {'x' : cursors[session['name']][0], 'y' : cursors[session['name']][1], 'user' : session['name']}, room=room)

@socketio.on('obj_scale')
def obj_scale(scale):
    images[scale['name']][0] = [scale['x'], scale['y']]
    emit('other_obj_scale', {'x' : scale['x'], 'y' : scale['y'], 'url' : scale['name']}, room=room)

@socketio.on('obj_rotate')
def obj_rotate(angle):
    images[angle['name']][2] = angle['angle']
    emit('other_obj_rotate', {'angle' : angle['angle'], 'url' : angle['name']}, room=room)

@socketio.on('obj_move')
def obj_move(coord):
    images[coord['name']][1] = [coord['x'], coord['y']]
    emit('other_obj_move', {'x' : coord['x'], 'y' : coord['y'], 'url' : coord['name']}, room=room)

@socketio.on('top_layer')
def top_layer(img):
    emit('other_top_layer', {'url' : img['name']}, room=room)

#Broken gallery things
@socketio.on('save')
def save(scr):
    for i in scr:
        print 'hi'
        screenshots[i] = scr[i]
        emit('post', screenshots)

if __name__ == '__main__':
    socketio.run(app)
