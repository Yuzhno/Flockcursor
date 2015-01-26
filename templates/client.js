var socket;

String.prototype.replaceAll = function(str1, str2, ignore) 
{
    return this.replace(new RegExp(str1.replace(/([\/\,\!\\\^\$\{\}\[\]\(\)\.\*\+\?\|\<\>\-\&])/g,"\\$&"),(ignore?"gi":"g")),(typeof(str2)=="string")?str2.replace(/\$/g,"$$$$"):str2);
} 

var sanitize = function(message) {
    if(message != null)
	return message.replaceAll('<', '#');
}

var remove_white = new fabric.Image.filters.RemoveWhite({
    threshold: 20,
    distance: 140
});

$(document).ready(function() {
    
    var cursors = new Object(); 
    var images = new Object(); 
    var selected = '';
    var screens = {};

    var canvas = new fabric.Canvas('main-area');
    // var image_canvas = new fabric.Canvas('main-area');
    socket = io.connect('http://' + document.domain + ':' + location.port);

    /*when user joins they will have chat access*/
    socket.on('join', function() {
	document.getElementById('chat-prompt').disabled = false;
    });

    /*user gets a chat name. triggers 'joined' python function*/
    socket.on('connect', function() {
	var input = sanitize(prompt("Enter your nickname!", ""));
	d = new Date();
	d1 = new Date();
	var img = canvas.toDataURL(d.toUTCString()+"/png");
	var img2 = canvas.toDataURL(d1.toUTCString()+"/png")
	screen['img1'] = ('<img src="'+img+'"/>');
	/*	console.log('<img src="'+img2+'"/>');
		console.log(screen['img1']);*/
	socket.emit('joined', {name : input});
    });

    socket.on('draw_all', function(e) {
	for (var key in e.players){
	    if (cursors[key] == undefined){
		cursors[key] = new fabric.Group(
		    [new fabric.Circle({ radius : 10, 
					 fill:'#f55',
					 originX: 'center',
					 originY: 'center'}),
		     new fabric.Text(key, { fontSize: 10,
					    originX: 'center',
					    originY: 'center'})],
		    { left : e.players[key][0], top : e.players[key][1] });
		cursors[key].lockMovementX = cursors[key].lockMovementY = true;
		cursors[key].lockRotation = true;
		cursors[key].lockScalingX = cursors[key].lockScalingY = true;
		cursors[key].hasBorders = cursors[key].hasControls = false;		    
		canvas.add(cursors[key]);
	    }
	}
    });

    socket.on('draw_one', function(e) {
	cursors[e.user] = new fabric.Group(
	    [new fabric.Circle({ radius : 10, 
				 fill:'#f55',
				 originX: 'center',
				 originY: 'center'}),
	     new fabric.Text(e.user, { fontSize: 10,
 				       originX: 'center',
				       originY: 'center'})],
	    { left : e.coord[0], top : e.coord[1] });
	cursors[e.user].lockMovementX = cursors[e.user].lockMovementY = true;
	cursors[e.user].lockRotation = true;
	cursors[e.user].lockScalingX = cursors[e.user].lockScalingY = true;
	cursors[e.user].hasBorders = cursors[e.user].hasControls = false;		    
	canvas.add(cursors[e.user]);
    });

    socket.on('remove', function(e) {
	canvas.remove(cursors[e.user]);
	delete cursors[e.user];
	canvas.renderAll();
    });

    socket.on('diffname', function(e) {
	sanitize(alert("This username is taken. Please select a new one."));
	if (e == undefined) {
	    var input = sanitize(prompt("Enter your nickname!", ""));
	}
	socket.emit('joined', {name : input});
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

    var mouse_last_move = 0;
    canvas.on('mouse:move', function(e) {
	if(Date.now() - mouse_last_move > 25){
	    var pointer = canvas.getPointer(e.e);
	    socket.emit('mouse_move', {top : pointer.x, left : pointer.y});
	    mouse_last_move = Date.now();
	}
    });

    canvas.on('object:selected', function(e) {
	selected = canvas.getActiveObject();
	//socket.emit('top_layer', {name : selected['name']});
    });

    //  socket.on('other_top_layer', function(e){
    //	canvas.bringForward(images[e.url]);
    //   });

    canvas.on('selection:cleared', function(e) {
	selected = '';
    });

    canvas.on('object:moving', function(e) {
	socket.emit('obj_move', {x : selected.getLeft(), y : selected.getTop(), name : selected['name']});
    });

    socket.on('other_obj_move', function(e){
	if(e.url != selected['name']) {
	    images[e.url].setLeft(e.x);
	    images[e.url].setTop(e.y);
	}
    });

    canvas.on('object:scaling', function(e) {
	socket.emit('obj_scale', {x : selected.getScaleX(), y : selected.getScaleY(), name : selected['name']});
    });

    socket.on('other_obj_scale', function(e){
	if(e.url != selected['name']) {
	    images[e.url].setScaleX(e.x);
	    images[e.url].setScaleY(e.y);
	}
    });

    canvas.on('object:rotating', function(e) {
	socket.emit('obj_rotate', {angle : selected.getAngle(), name : selected['name']});
    });

    socket.on('other_obj_rotate', function(e){
	if(e.url != selected['name']) {
	    images[e.url].setAngle(e.angle);
	}
    });

    socket.on('move_clientmouse', function(e){
	cursors[e.user].set('left' , e.x);
	cursors[e.user].set('top' , e.y);			    
	canvas.renderAll();
    });

    socket.on('render_image', function(e){
	fabric.Image.fromURL(e.url, function(img) {
	    img.scale(0.4).set({
		left: 10,
		top : 10 });
	    img['name'] = e.url;
	    images[e.url] = img;
	    canvas.add(img);
	    canvas.renderAll();
	});
    });
});
