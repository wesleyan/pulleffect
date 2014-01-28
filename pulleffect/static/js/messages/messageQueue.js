
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

var displayMessages = function(messages){

	var panel = $("<div />").width("300px");
	panel.addClass("panel panel-default")
	var table = $("<table />").addClass("table table-striped table-condensed");

	messages = sampleMessages;

	var maxMessages = 5

	for(var i = 0; i < messages.length && i < maxMessages; i++){
		var row = $('<tr />');

		if (messages[i].severity == 3 || messages[i].severity == 4)
			row.addClass("text-warning");
		else if (messages[i].severity == 5)
			row.addClass("text-danger");



		row.append($('<td />').text(messages[i].device))

		var icon;
		switch (messages[i].device_type){
			case "mac": icon = "fa fa-apple"; break;
			case "pc": icon = "fa fa-windows"; break;
			case "printer": icon = "fa fa-print"; break;
			case "roomtrol": icon = "fa fa-flash"; break;
			default: icon = "";
		}
		
		row.append($('<td />').append($('<span />').addClass(icon)));
		row.append($('<td />').text(messages[i].location));
		row.append($('<td />').text(messages[i].title));
		row.append($('<td />').text(messages[i].description));
		row.append($('<td />').text(messages[i].time));


		table.append(row);
	}


	panel.append(table);
	$('.content').append(panel);
}
