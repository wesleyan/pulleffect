var getGcalList = function() {
    // $.get( '/gcal/get_calendar_list', renderGcalList);
    $.ajax({
        type: 'GET',
        url: '/gcal/get_calendar_list',
        success: renderGcalList
    });
}

var refreshGcalList = function() {
    $.getJSON('/gcal/refresh_calendar_list')
    .success(function(gcal_list){
        renderGcalList(gcal_list);
    }).error(function(err){
        console.log(err);
    });
}

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