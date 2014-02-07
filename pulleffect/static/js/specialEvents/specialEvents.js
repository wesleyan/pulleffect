
var loadEventTable = function(event, cb){

	var eventItem = $('<li />').addClass('list-group-item').css('font-size', '12px');

	eventItem.append($('<div />').html(htmlspecialchars_decode(htmlspecialchars_decode(event.title,' ENT_NOQUOTES'))).css('border-bottom', '1px solid #aaa'));
  eventItem.css('background-color', '#FFFFFF');

	var timeDiv = $('<div />');
	timeDiv.append('<b>' + moment(event.start).format('hh:mm A') + '</b> ');
	timeDiv.append('<i>' + moment(event.eventStart).format('hh:mm A') + '</i>');
	timeDiv.append(' <i class="fa fa-long-arrow-right"></i> ');
	timeDiv.append('<i>' + moment(event.eventEnd).format('hh:mm A') + '</i> ');
	timeDiv.append('<b>' + moment(event.end).format('hh:mm A') + '</b>');

	timeDiv.css('border-bottom', '1px solid #aaa');
	eventItem.append(timeDiv);


	var techList = []
	for (var i = 0; i < event.shifts.length; i++){
		techList.push(event.shifts[i].staff);
	}

	techString = techList.join(', ');
	eventItem.append($('<div />').html(techString));

	if (event.cancelled){
		eventItem.css('background-color', '#FFABAB');
	}

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
  panel.css('background-color', '#FFFFFF');
	var eventsList = $("<ul />").addClass("eventsList").addClass('list-group ')
	panel.append(eventsList);


	// var startTime = moment().startOf('day').unix();
	// var endTime = moment().endOf('day').unix();

	// $.getJSON('http://ims-dev.wesleyan.edu:8080/api/events?start='+startTime + 'end=' + endTime )
	// 	.success(renderSpecialEvents)
	// 	.error(function(err){
 //        	console.log(err);
 //    });

  $.getJSON('http://ims-dev.wesleyan.edu:8080/api/events?minutes=3000')
    .success(renderSpecialEvents)
    .error(function(err){
          console.log(err);
    });

	// $('.Widgets').append(panel);
  gridster.add_widget(panel);
}



function htmlspecialchars_decode (string, quote_style) {
  // From: http://phpjs.org/functions
  // +   original by: Mirek Slugen
  // +   improved by: Kevin van Zonneveld (http://kevin.vanzonneveld.net)
  // +   bugfixed by: Mateusz "loonquawl" Zalega
  // +      input by: ReverseSyntax
  // +      input by: Slawomir Kaniecki
  // +      input by: Scott Cariss
  // +      input by: Francois
  // +   bugfixed by: Onno Marsman
  // +    revised by: Kevin van Zonneveld (http://kevin.vanzonneveld.net)
  // +   bugfixed by: Brett Zamir (http://brett-zamir.me)
  // +      input by: Ratheous
  // +      input by: Mailfaker (http://www.weedem.fr/)
  // +      reimplemented by: Brett Zamir (http://brett-zamir.me)
  // +    bugfixed by: Brett Zamir (http://brett-zamir.me)
  // *     example 1: htmlspecialchars_decode("<p>this -&gt; &quot;</p>", 'ENT_NOQUOTES');
  // *     returns 1: '<p>this -> &quot;</p>'
  // *     example 2: htmlspecialchars_decode("&amp;quot;");
  // *     returns 2: '&quot;'
  var optTemp = 0,
    i = 0,
    noquotes = false;
  if (typeof quote_style === 'undefined') {
    quote_style = 2;
  }
  string = string.toString().replace(/&lt;/g, '<').replace(/&gt;/g, '>');
  var OPTS = {
    'ENT_NOQUOTES': 0,
    'ENT_HTML_QUOTE_SINGLE': 1,
    'ENT_HTML_QUOTE_DOUBLE': 2,
    'ENT_COMPAT': 2,
    'ENT_QUOTES': 3,
    'ENT_IGNORE': 4
  };
  if (quote_style === 0) {
    noquotes = true;
  }
  if (typeof quote_style !== 'number') { // Allow for a single string or an array of string flags
    quote_style = [].concat(quote_style);
    for (i = 0; i < quote_style.length; i++) {
      // Resolve string input to bitwise e.g. 'PATHINFO_EXTENSION' becomes 4
      if (OPTS[quote_style[i]] === 0) {
        noquotes = true;
      } else if (OPTS[quote_style[i]]) {
        optTemp = optTemp | OPTS[quote_style[i]];
      }
    }
    quote_style = optTemp;
  }
  if (quote_style & OPTS.ENT_HTML_QUOTE_SINGLE) {
    string = string.replace(/&#0*39;/g, "'"); // PHP doesn't currently escape if more than one 0, but it should
    // string = string.replace(/&apos;|&#x0*27;/g, "'"); // This would also be useful here, but not a part of PHP
  }
  if (!noquotes) {
    string = string.replace(/&quot;/g, '"');
  }
  // Put this in last place to avoid escape being double-decoded
  string = string.replace(/&amp;/g, '&');

  return string;
}