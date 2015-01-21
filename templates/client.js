var socket;

var sanitize = function(message) {
    if(message != null)
	return message.replace('<', '#');
}

$(document).ready(function() {
    
    var cursors = new Object(); 

    var canvas = new fabric.Canvas('main-area');
    socket = io.connect('http://' + document.domain + ':' + location.port);

    /*when user joins they will have chat access*/
    socket.on('join', function() {
	document.getElementById('chat-prompt').disabled = false;
    });

    /*user gets a chat name. triggers 'joined' python function*/
    socket.on('connect', function() {
	var input = sanitize(prompt("Enter your nickname!", ""));
	socket.emit('joined', {name : input});
    });

    socket.on('draw_all', function(e) {
	for (var key in e.players){
	    cursors[key] = new fabric.Group(
		[new fabric.Circle({ radius : 10, 
				     fill:'#f55'}),
		 new fabric.Text(key, { fontSize: 10,
					originX: 'center',
					originY: 'center'})],
		{ left : e.players[key][0], top : e.players[key][1] });
	    canvas.add(cursors[key]);
	}
    });

    socket.on('remove', function(e) {
	delete cursors[e.user];
	canvas.renderAll();
    });

    /*when user types in chat*/
    $('#chat-prompt').keypress(function(e) {
	var code = e.keyCode || e.which;
	if (code == 13) {
	    text = sanitize($('#chat-prompt').val());
	    $('#chat-prompt').val('')

	    socket.emit('user_msg', {message: text});
	}
    });

    /*when user types in nickname area*/
    $('#name').keypress(function(e) {
	var code = e.keyCode || e.which;
	if (code == 13) {
	    text = sanitize($('#name').val());
	    $('#name').val('');
	    socket.emit('change_name', {new: text});
	}
    });

    /*updates chat and users online*/
    socket.on('msg', function(data) {
	var new_msg = document.createElement('p');
	if (data.message != undefined) {
	    new_msg.innerHTML = data.message;
	    $('#interface').append(new_msg);
	}
	if (data.online != undefined) {
	    document.getElementById("online").innerHTML = data.online + " user(s) online";
	}	
	/*Auto Scroll*/
	$('#interface').scrollTop($('#interface')[0].scrollHeight);

    });

    $('canvas').mousemove(function(e) {
	x = e.pageX;
	y = e.pageY;
	socket.emit('mouse_move', {top : x , left : y});
    });

    socket.on('move_clientmouse', function(x, y, user){
	cursors[user].set('left' , x);
	cursors[user].set('top' , y);
	canvas.renderAll();
    });
});
