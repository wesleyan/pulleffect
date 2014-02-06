
var loadEventTable = function(event, cb){

	var eventItem = $('<li />').addClass('list-group-item').css('font-size', '12px');
	eventItem.append($('<div />').html(event.title).css('border-bottom', '1px solid #aaa'));

	var timeDiv = $('<div />');
	timeDiv.append('<b>' + moment(event.start).format('hh:mm A') + '</b> ');
	timeDiv.append('<i>' + moment(event.eventStart).format('hh:mm A') + '</i>');
	timeDiv.append(' <i class="fa fa-long-arrow-right"></i> ');
	timeDiv.append('<i>' + moment(event.eventEnd).format('hh:mm A') + '</i> ');
	timeDiv.append('<b>' + moment(event.end).format('hh:mm A') + '</b>');

	eventItem.append(timeDiv);

	if (event.cancelled){
		eventItem.css('background-color', '#FFABAB');
	}

	eventItem.hover(function(){$(this).css('background-color', '#eee');}, 
					function(){$(this).css('background-color', '#fff')});
		

	if (typeof cb === 'function')
		cb(eventItem);
}

var renderSpecialEvents = function(events){
	for (var i = 0; i < events.length; i++){
		loadEventTable(events[i], function(eventTable){
			$(".eventsList").prepend(eventTable)
		});
	}
}

var renderSpecialEventsWidget = function(){

	var panel = $("<div />").width("300px").height('200px').css('overflow', 'auto').css('margin-top', '10px');
	panel.addClass("panel panel-default");
	var eventsList = $("<ul />").addClass("eventsList").addClass('list-group ')
	panel.append(eventsList);

	$.getJSON('http://ims-dev.wesleyan.edu:8080/api/events?minutes=20000')
		.success(renderSpecialEvents)
		.error(function(err){
        	console.log(err);
    });

	$('.Widgets').append(panel);
}