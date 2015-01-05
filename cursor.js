
var c = document.getElementById("myCanvas");
var ctx = c.getContext("2d");

var shape = function Shape(x, y, w, h, fill) {
    this.x = x || 0;
    this.y = y || 0;
    this.w = w || 1;
    this.h = h || 1;
    this.fill = fill || '#AAAAAA';
}

Shape.prototype.draw = function(ctx) {
    ctx.fillStyle = this.fill;
    ctx.fillRect(this.x, this.y, this.w, this.h);
}


$(document).ready(start);

var start = function(){
    var socket = io.connect('http://' + document.domain + ':' + location.port);
    socket.on('connect', function(msg) {
	$('#log').append(msg.data);
    });
    socket.emit('my event', {data: 'I\'m connected!'});

}
