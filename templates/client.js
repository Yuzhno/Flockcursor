var socket;
var number; 

$(document).ready(function() {
    socket = io.connect('http://' + document.domain + ':' + location.port);

    socket.on('connect', function() {
	socket.emit('joined', {});
    });

    $('#chat-prompt').keypress(function(e) {
        var code = e.keyCode || e.which;
        if (code == 13) {
            text = $('#chat-prompt').val();
            $('#chat-prompt').val('');
            socket.emit('user_msg', {message: text});
        }
    });

    $('#name').keypress(function(e) {
        var code = e.keyCode || e.which;
        if (code == 13) {
            text = $('#name').val();
            $('#text').val('');
            socket.emit('change_name', {new: text});
        }
    });

    socket.on('msg', function(data) {
	console.log(data);
	var new_msg = document.createElement('p');
	new_msg.innerHTML = data.message;
        $('#interface').append(new_msg);
    });
    $('#main-area').mousemove(function(e) {
	var x = e.clientX;
 	var y = e.clientY;
	socket.emit('mousemove', {x : x , y : y});
    });
    socket.on('movemouse', function(x , y , user){
	//socket.emit('mousemove' , {x : x , y : y , user : user});
	console.log('a');
    });
});
