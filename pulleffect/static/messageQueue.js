
var sampleMessages = [
	{device: "name1", device_type: "mac", location:"SCIE 127", severity: 1, 
	 title: "Turning off", description: "Turning off", time: "12:00"},
	 {device: "name2", device_type: "pc", location:"SCIE 127", severity: 2, 
	 title: "Turning off", description: "Turning off", time: "12:00"},
	 {device: "name3", device_type: "roomtrol", location:"SCIE 127", severity: 3, 
	 title: "Turning off", description: "Turning off", time: "12:00"},
	 {device: "name4", device_type: "printer", location:"SCIE 127", severity: 4,
	 title: "Turning off", description: "Turning off", time: "12:00"},
	 {device: "name5", device_type: "roomtrol", location:"SCIE 127", severity: 5, 
	 title: "Turning off", description: "Turning off", time: "12:00"}
];



var formRow = function(message, cb){
	var row = $('<tr />');
	row.css({fontSize: "11px"});

	if (message.severity == 3 || message.severity == 4)
		row.addClass("text-warning");
	else if (message.severity == 5)
		row.addClass("text-danger");

	row.append($('<td />').text(message.device))


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
	row.append($('<td />').text(message.time));



	if (typeof cb === 'function'){
		cb(row);
	}
}

var addRow = function(){

	var lastRow = $("table tr:last-child");

	lastRow.children('td').animate({padding: 0})
		.wrapInner('<div />')
		.children()
		.slideUp(200, function(){
			$(this).parent().parent().remove();
		});


	var newRow = $("<tr />");
	newRow.append($("<td>HERE</td>"));
	newRow.children().animate({padding:0}).wrapInner("<div />");
	newRow.children().children().css({display: 'none'});//.text("HERE");
	$("table").prepend(newRow);
	newRow.children().children().slideDown(300, function(){

	});


}

var displayMessages = function(messages){

	var panel = $("<div />").width("300px");
	panel.addClass("panel panel-default")
	var table = $("<table />").addClass("table table-condensed");

	messages = sampleMessages;

	var maxMessages = 5

	for(var i = 0; i < messages.length && i < maxMessages; i++){

		formRow(messages[i], function(row){
			table.append(row);
		});

	}

	panel.height('200px');
	panel.append(table);
	bt = $("<button />").attr("type", "button").addClass("btn btn-success").text("Update").click(addRow);
	bt.css({bottom: "0px"});
	panel.append(bt);
	$('.Widgets').append(panel);
}
