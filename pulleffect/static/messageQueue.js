
var sampleMessages = [
	{device: "name1", device_type: "mac", location:"SCIE 127", severity: 1, 
	 title: "Turning off", description: "Turning off", time: "12:00"},
	 {device: "name2", device_type: "mac", location:"SCIE 127", severity: 3, 
	 title: "Turning off", description: "Turning off", time: "12:00"},
	 {device: "name1", device_type: "mac", location:"SCIE 127", severity: 5, 
	 title: "Turning off", description: "Turning off", time: "12:00"}
];

var displayMessages = function(messages){

	var panel = $("<div />");
	var table = $("<table />");

	messages = sampleMessages;

	var maxMessages = 5

	for(var i = 0; i < messages.length && i < maxMessages; i++){
		var row = $('<tr />');

		if (messages[i].severity == 3 || messages[i].severity == 4)
			row.addClass("text-warning");
		else if (messages[i].severity == 5)
			row.addClass("text-danger");



		row.append($('<td />').text(messages[i].device))
		row.append($('<td />').text(messages[i].device_type));
		row.append($('<td />').text(messages[i].location));
		row.append($('<td />').text(messages[i].title));
		row.append($('<td />').text(messages[i].description));
		row.append($('<td />').text(messages[i].time));


		table.append(row);
	}


	panel.append(table);
	$('.Widgets').append(panel);
}
