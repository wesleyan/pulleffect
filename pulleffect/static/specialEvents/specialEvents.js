
var loadEventTable = function(event, cb){

	var eventItem = $('<li />').addClass('list-group-item').css('font-size', '12px');
	eventItem.append($('<div />').html(event.title).css('border-bottom', '1px solid #EEE'));
	var timeStr =  moment(event.start).format('hh:mm A') + '-' + moment(event.end).format('hh:mm A');
	eventItem.append($('<div />').html(timeStr));
	

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

	$.getJSON('http://ims-dev.wesleyan.edu:8080/api/events?minutes=5000')
		.success(renderSpecialEvents)
		.error(function(err){
        	console.log(err);
    });

	$('.Widgets').append(panel);
}