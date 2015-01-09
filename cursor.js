

var c = document.getElementById("myCanvas");
var ctx = c.getContext("2d");

function Shape(x, y, w, h, fill) {
    this.x = x || 0;
    this.y = y || 0;
    this.w = w || 1;
    this.h = h || 1;
    this.fill = fill || '#AAAAAA';
};

Shape.prototype.draw = function(ctx) {
    ctx.fillStyle = "#FF0000";
    ctx.fillRect(100, 100, 100, 100);
};

ctx.fillStyle = "#FF0000";
ctx.fillRect(0,0,150,75);

c.addShape(new Shape (100 , 100 ,100 ,100 , "#FF0000"));

var start = function(){
    var socket = io.connect('http://' + document.domain + ':' + location.port);
    socket.on('connect', function(msg) {
	$('#log').append(msg.data);
    });
    socket.emit('my event', {data: 'I\'m connected!'});

};
