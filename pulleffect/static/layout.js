
        {# Alert stuff #}
        console.log("HERE");
        // A helper function for displayAlerts function
        var getAlertType = function(alert) {
            switch (alert[0]) {
                case 'success':
                    return 'success';
                case 'error':
                    return 'danger';
                case 'warning':
                    return 'warning';
                default:
                    return 'info';
            }
        }
        // Display alerts after events
        var displayAlerts = function(alerts) {
            if (alerts.length == 0)
                return;

            var alert;

            for (var i = 0; alerts.length > i; i++) {
                alert = $('<div class="alert alert-' + getAlertType(alerts[i]) + '"><button type="button" class="close" data-dismiss="alert" aria-hidden="true">&times;</button>' + alerts[i][1] + '</div>')
                    .hide()
                    .delay(500 * (i))
                    .slideDown(500)
                    .delay(10000 * (i + 1))
                    .slideUp(500, function() {
                        $(this).remove();
                    });
                $('#alerts').append(alert);
            }
        }
        {# End alert stuff #}

        {# User authentication stuff #}
        // Sign in Pull Effect user
        var signIn = function() {
            var username = $("input[name='username']").val();
            var password = $("input[name='password']").val();
            $.ajax({
                type: "POST",
                url: "{{ url_for('user.signin') }}",
                data: JSON.stringify({
                    u: username,
                    p: password
                }),
                contentType: 'application/json;charset=UTF-8',
                success: function(result) {
                    if (result.alert)
                        return displayAlerts(result.alert);
                    if (result.redirect)
                        return window.location.replace(result.redirect);
                    return;
                },
                error: function(err) {
                    return displayAlerts([
                        ['error', 'We seem to have encountered an unexpected error! Please try again or contact the management.']
                    ]);
                }
            });
        }
        {# End user authentication stuff #}

        {# Configuration stuff #}
        {% if session.signed_in %}
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
        {% endif %}

        $(function() {
            displayAlerts({{ get_flashed_messages(with_categories = true) | tojson }});
            getGoogleCalendarList();
        });


       
        // if (!{{dashboard | tojson}}.gen_prefs.options){
        //             $('.flap>span')
        //                 .removeClass('open-drawer')
        //                 .addClass('close-drawer')
        //                 .tooltip('hide')
        //                 .attr('data-original-title', 'Close Drawer')
        //                 .tooltip('fixTitle')
        //                 .tooltip('show');
        //             }

        {# End configuration stuff #}

        {#config_panel#}

        dash = {{dashboard | tojson}}
        $("#configure").on('hide.bs.modal', function (e) {
            
            dash.gen_prefs.config_panel = false;
            console.log(dash.gen_prefs.config_panel);

            updateCookies()
       });
        $("#configure").on('show.bs.modal', function (e) {
        
            dash.gen_prefs.config_panel = true;
            console.log(dash.gen_prefs.config_panel);

            updateCookies();
            console.log(getCookie());
        });

        var updateCookies = function(){
            document.cookie = "dashboard=" + JSON.stringify(dash);
        }

        var getCookie = function(){
                return $.parseJSON(document.cookie.substring(10, document.cookie.length));
        }



        {# Drawer stuff #}
        // Navbar drawer function
        $('.flap>span').click(function() {

            // Close drawer
            if ($('.flap>span').hasClass('close-drawer')) {
                $('nav:first').css({
                    'min-height': '0px'
                }).slideUp(250, function() {
                    $('.flap>span')
                        .removeClass('close-drawer')
                        .addClass('open-drawer')
                        .tooltip('hide')
                        .attr('data-original-title', 'Open Drawer')
                        .tooltip('fixTitle')
                        .tooltip('show');
                });
            }

            // Open drawer
            else {
                $('nav:first').slideDown(250, function() {
                    $(this).css({
                        'min-height': '50px'
                    });
                    $('.flap>span')
                        .removeClass('open-drawer')
                        .addClass('close-drawer')
                        .tooltip('hide')
                        .attr('data-original-title', 'Close Drawer')
                        .tooltip('fixTitle')
                        .tooltip('show');
                });
            }
        });
        {# End drawer stuff #}
