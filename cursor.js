
$(document).ready(start);

var start = function(){
    var socket = io.connect('http://' + document.domain + ':' + location.port);
    socket.on('connect', function(msg) {
	$('#log').append(msg.data);
    });
    socket.emit('my event', {data: 'I\'m connected!'});

}
