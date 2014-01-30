
////Sample messages for testing purposes
var sampleMessages = [
	{device: "name5", device_type: "mac", location:"SCIE 127", severity: 1, 
	 title: "Turning off", description: "Turning off", time: 50000},
	 {device: "name4", device_type: "pc", location:"SCIE 127", severity: 2, 
	 title: "Turning off", description: "Turning off", time: 40000},
	 {device: "name3", device_type: "roomtrol", location:"SCIE 127", severity: 3, 
	 title: "Turning off", description: "Turning off", time: 30000},
	 {device: "name2", device_type: "printer", location:"SCIE 127", severity: 4,
	 title: "Turning off", description: "Turning off", time: 20000},
	 {device: "name1", device_type: "roomtrol", location:"SCIE 127", severity: 5, 
	 title: "Turning off", description: "Turning off", time: 10000}
];

var newMessages = [
	{device: "name10", device_type: "roomtrol", location:"SCIE 127", severity: 2, 
	 title: "Turning off", description: "Turning off", time: 100000},
	{device: "name9", device_type: "roomtrol", location:"SCIE 127", severity: 3, 
	 title: "Turning off", description: "Turning off", time: 90000},
	{device: "name8", device_type: "roomtrol", location:"SCIE 127", severity: 4, 
	 title: "Turning off", description: "Turning off", time: 80000},
	{device: "name7", device_type: "roomtrol", location:"SCIE 127", severity: 5, 
	 title: "Turning off", description: "Turning off", time: 70000},
	{device: "name6", device_type: "roomtrol", location:"SCIE 127", severity: 5, 
	 title: "Turning off", description: "Turning off", time: 60000},
	{device: "name5", device_type: "mac", location:"SCIE 127", severity: 1, 
	 title: "Turning off", description: "Turning off", time: 50000},
	 {device: "name4", device_type: "pc", location:"SCIE 127", severity: 2, 
	 title: "Turning off", description: "Turning off", time: 40000}
];

var lastMessageDisplayed = null;

//////////////////////////////////////////////////////////////////////////////////////
// Update is called with the result of the ajax request which gets messages after
// the table is initially rendered with the starting set of messages.
//////////////////////////////////////////////////////////////////////////////////////
var updateMessageQueue = function(messages){

	//Forms a list of the messages which have not yet been displayed
	var newMessageList = [];
	var i = 0;
	while(messages[i].time != lastMessageDisplayed.time){
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


	renderMessages(sampleMessages, table);
	panel.append(table);



	$('.Widgets').append(panel);

	//Only to test the update functionality.
	setTimeout(function(){updateMessageQueue(newMessages)}, 1000);
}

//Once max gets this working......
var pullMessages = function(){
	$.ajax({
        type: 'GET',
        url: '/messages/',
        success: function(messages){
        	console.log(messages);

        },
        error: function(err) {
            console.log(err);
        }
    });
}
