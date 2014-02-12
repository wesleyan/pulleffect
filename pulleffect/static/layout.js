var getGoogleCalendarList = function() {
    $.ajax({
        type: "GET",
        url: "{{ url_for('gcal.get_calendar_list') }}",
        success: displayCalendarList,
        error: function(err) {
            console.log(err);
        }
    });
}

var refreshGoogleCalendarList = function() {
    $.ajax({
        type: "GET",
        url: "{{ url_for('gcal.refresh_calendar_list') }}",
        success: displayCalendarList,
        error: function(err) {
            console.log(err);
        }
    });
}

var getGoogleCalendarEvents = function(){
    $.ajax({
        type: "GET",
        url: "{{ url_for('gcal.get_calendar_events') }}",
        success: displayEvents,
        error: function(err) {
            console.log(err);
        }
    });
}

var displayEvents = function(response){
    console.log(response);
}

var displayCalendarList = function(response) {
    if (response.error === 'AccessTokenRefreshError') {
        return displayAlerts([
            ['error', 'Sorry! We need you to authenticate your account with Google Calendar again!']
            ]);
    }
    if (response.calendars) {        
        var calendars = response.calendars;
        var btn_group_vertical = $('<div/>', {'class': 'btn-group-vertical', 'data-toggle':'buttons'});

        for (var i = 0; i < calendars.length; i++) {
            btn_group_vertical.append('<div class="checkbox btn btn-info"><label><input class="hidden" type="checkbox" value="' + calendars[i].calendar_id + '">' + calendars[i].calendar_name + '<label></div>');
        }
        $('#google_calendar_list').empty().attr('id', '#google_calendars').append(btn_group_vertical);
        return;
    } 
    return displayAlerts([
        ['error', 'Sorry! We seem to have encountered an unknown error!']
        ]);
}