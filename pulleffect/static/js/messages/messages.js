
var lastMessageDisplayed = null;

var getNewMessages = function(){
		$.getJSON('/messages/').success(updateMessageQueue).error(function(err){
        	console.log(err);
        });
        setTimeout(getNewMessages, 5000);

}

//////////////////////////////////////////////////////////////////////////////////////
// Update is called with the result of the ajax request which gets messages after
// the table is initially rendered with the starting set of messages.
//////////////////////////////////////////////////////////////////////////////////////
var updateMessageQueue = function(messages){

	//Forms a list of the messages which have not yet been displayed
	var newMessageList = [];
	var i = 0;
	while(messages.length > 0 && messages[i].time != lastMessageDisplayed.time){
		newMessageList.push(messages[i]);
		i++;
	}

	newMessageList = newMessageList.reverse();

	// Adds each element of the new message list to the table asynchronously, so each row
	// has time to animate.
	i = 0;
	var addNewMessages = function(){
		if(i >= newMessageList.length){return;} 
		lastMessageDisplayed = newMessageList[i]
		addRow(newMessageList[i]);
		i++;
		//Set waits 100 miliseconds longer than it takes to add a row to the list
		setTimeout(addNewMessages, 500)	

	}

	addNewMessages();
}


//////////////////////////////////////////////////////////////////////////////////////
// formRow takes in a message and creates a table row.
//
// callback(newRow)
//////////////////////////////////////////////////////////////////////////////////////
var formRow = function(message, cb){
	var row = $('<tr />');
	row.css({fontSize: "11px"});

	if (message.severity == 3 || message.severity == 4)
		row.addClass("text-warning");
	else if (message.severity == 5)
		row.addClass("text-danger");

	row.append($('<td />').text(message.device))

	//choses the icon for each device type
	switch (message.device_type){
		case "mac": var icon = "fa fa-apple"; break;
		case "pc": var icon = "fa fa-windows"; break;
		case "printer": var icon = "fa fa-print"; break;
		case "roomtrol": var icon = "fa fa-flash"; break;
		default: var icon = "";
	}
	
	row.append($('<td />').append($('<span />').addClass(icon)));
	row.append($('<td />').text(message.location));
	row.append($('<td />').text(message.title));
	row.append($('<td />').text(message.description));
	row.append($('<td />').text(moment.unix(message.time).format("hh:mm A")));

	if (typeof cb === 'function'){
		cb(row);
	}
}

//////////////////////////////////////////////////////////////////////////////////////
// addRow takes in a message and animates the addition of a new row created by that 
// message (and possibly the removal of the last row in the list as well).
//////////////////////////////////////////////////////////////////////////////////////
var addRow = function(message, cb){

	//This would remove the last row of the list if we didn't want it to be scrollable...
	// var lastRow = $(".messageTable tr:last-child").addClass("lastRow");
	// $(".lastRow").children('td').animate({padding: 0})
	// 	.wrapInner('<div />')
	// 	.children()
	// 	.slideUp(400, function(){
	// 		$(this).parent().parent().remove();
	// 	});
	
	//Animates new row by initially hiding it and then using jquery's slide down animation
	formRow(message, function(newRow){
		newRow.children().wrapInner("<div />");
		newRow.children().children().css({display: 'none'});
		$(".messageTable").prepend(newRow);
		newRow.children().children().slideDown(400, function(){
			if ($(this).parent().is(":last-child")){
				if (typeof cb === 'function'){
					cb()
				}
			}
		});
	});
}

//////////////////////////////////////////////////////////////////////////////////////
// Renders messages the first time the table is loaded. This adds all messages
// returned by the messages route without animation. 
//////////////////////////////////////////////////////////////////////////////////////
var renderMessages = function(messages, table){

	messages = messages.reverse();
	for(var i = 0; i < messages.length; i++){

		lastMessageDisplayed = messages[i];

		formRow(messages[i], function(row){
			
			table.prepend(row);
		});
	}
}

//////////////////////////////////////////////////////////////////////////////////////
// Creates the widget panel and table programmatically and does everything else from t
//////////////////////////////////////////////////////////////////////////////////////
var renderMessageQueue = function(){


	var panel = $("<div />").width("400px");
	panel.addClass("panel panel-default");
	panel.height('200px').css({overflow: "auto"});

	var table = $("<table />").addClass("table table-condensed  messageTable");




	$.getJSON('/messages/').success(function(messages){
        	renderMessages(messages, table);
        }).error(function(err){
        	console.log(err);
        });


	panel.append(table);

	// $('.Widgets').append(panel);
	gridster.add_widget(panel);

	//Only to test the update functionality.
	setTimeout(getNewMessages, 60000);
}

