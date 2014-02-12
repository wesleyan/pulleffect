
    var getGoogleCalendarEvents = function() {
        newCal = {calID: $('label.active input').val()};

        $.ajax({
            type: "GET",
            url: "{{ url_for('gcal.get_calendar_events') }}?cal_id=" + newCal.calID,
            success: displayEvents
        });
    }

    var displayEvents = function(response) {
        console.log(response);
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