
// Gets list of Google calendars for user, then fires render function
var getGcalList = function() {
    $.ajax({
        type: 'GET',
        url: '/gcal/get_calendar_list',
        success: renderGcalList
    });
}

// Refreshes list of Google calendars for user, then fires render function
var refreshGcalList = function() {
    $.getJSON('/gcal/refresh_calendar_list')
    .success(function(gcal_list){
        renderGcalList(gcal_list);
    }).error(function(err){
        console.log(err);
    });
}

// Gets events for a given Google calendar, then fires render function
var getGcalEvents = function() {
    newCal = {calID: $('label.active input').val()};

    $.ajax({
        type: "GET",
        url: "/gcal/get_calendar_events?cal_id=" + newCal.calID,
        success: displayEvents
    });
}

// Renders list of Google calendars in a (given?) Google calendar widget
var renderGcalList = function(response) {
    if (response.error == true) {
        displayAlerts('error', 'There\'s an error displaying calendars. Try authenticating again?');
        $('#calendars').hide()
        $('#google_authenticate').show()
    }
    if (response.calendars) {        
        var calendars = response.calendars;
        var btn_group_vertical = $('<div/>', {'class': 'btn-group-vertical', 'data-toggle':'buttons'});

        for (var i = 0; i < calendars.length; i++) {
            btn_group_vertical.append('<label class="btn btn-primary"><input type="radio" name="options" id="option1" value="' + calendars[i].calendar_id + '">' + calendars[i].calendar_name + '</label>')
        }
        $('#google_calendar_list').empty().attr('id', '#google_calendars').append(btn_group_vertical);
        return;
    } 
    return displayAlerts('error', 'Sorry! We seem to have encountered an unknown error!');
}

// Renders table of Google calendar events in a (given?) Google calendar widget
var renderGcalEvents = function(response) {
    loadWidget();

    var events = response.calendar_events.items;

    $("#eventsTable").empty();

    if (events.length == 0){
        $('#eventsTable').replaceWith($('<span/>').append($('<h3/>', {"class":"centered"}).text("YOU DONE FUCKED UP")));
    }

    var timeFormat = "MM/DD  h:mm A";

    for (i = 0; i < 10 && i < events.length; i++) {
        var tableRow = $('<tr/>', {"class": "event"});
        var summaryCell = $('<td/>');
        var beginCell = $('<td/>');
        var endCell = $('<td/>');

        var summary = events[i].summary;
        var start = events[i].start.dateTime;
        var end = events[i].end.dateTime;

        tableRow
        .append(summaryCell.text(summary))
        .append(beginCell.text(moment(start).format(timeFormat)))
        .append(endCell.text(moment(end).format(timeFormat)));

        $("#eventsTable").append(tableRow);
    }
}

// Renders a Google calendar widget
var renderGcalWidget = function(){

    var refresh_button = $('<button />', 
    {
        'type':'submit', 
        'class': 'btn btn-success pull-right',
        'title': 'Refresh List',
        'alt': 'Refresh List'
    })
    .append($('<span />').addClass('fa fa-refresh'))
    .click(refreshGcalList);

    var gcal_list = $('<div />').addClass('google_calendar_list');

    var widget = $('<div />')
    .addClass('panel panel-default google_config')
    .css({'height': '300px', 'width': '300px'})
    .append(refresh_button)
    .append(gcal_list);

    gridster.add_widget(widget);
}

// Not sure what this one does yet, but it was related to Google calendar events.
var loadWidget = function(){
    var panel = $("<div />").width("300px");
    panel.addClass("panel panel-default")
    var loginForm = $("<form />", {"action":"{{ url_for('gcal.authenticate') }}", "method":"get", "role":"form"})
    var loginButton = $("<button />", {"type":"submit", "class":"btn btn-info center-block fa fa-calendar", "title":"Google Calendar", "alt":"Google Calendar"})
    // '<form action="{{ url_for("gcal.authenticate") }}" method="get" role="form"><button type="submit" class="btn btn-info center-block" title="Google Calendar" alt="Google Calendar"><span class="fa fa-calendar" /> Google Calendar</button></form>'
    var table = $("<table />").addClass("table table-striped table-condensed");

    var calendar = $('<div/>', {"class": "panel panel-default col-md-4", "id":"calendar"});
    var table = $('<table/>', {"class":"table table-striped", "id":"eventsTable"});
    calendar.append(table);

    loginForm.append(loginButton)
    panel.append(loginForm)
    $('.content').append(panel);
}