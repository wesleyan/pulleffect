
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

    var displayAlerts = function(alertType, alertMessage) {
        if (!alertMessage)
            return;
        var alert = $('<div class="alert alert-' + getAlertType([alertType]) + '"><button type="button" class="close" data-dismiss="alert" aria-hidden="true">&times;</button>' + alertMessage + '</div>')
        .hide()
        .delay(500)
        .slideDown(500)
        .delay(10000)
        .slideUp(500, function() {
            $(this).remove();
        });
        $('#alerts').append(alert);
    }

    // TODO: This will probably need to be moved into a general page load function so 
    // we don't need to keep adding stuff here
    $(function() {
        // Display alerts
        displayAlerts({{ get_flashed_messages(with_categories = true) | tojson }});

        {% if session.signed_in %}
            // Refresh google calendar list
            refreshGoogleCalendarList();
           {% endif %}
        });


    $("#configure").on('hide.bs.modal', function (e) {
        if (localStorage.getItem('config_open') == 'true' || localStorage.getItem('config_open') == null) {
            localStorage.setItem('config_open', 'false');
        }
    });

    $("#configure").on('show.bs.modal', function (e) {
        if (localStorage.getItem('config_open') == 'false' || localStorage.getItem('config_open') == null) {
            localStorage.setItem('config_open', 'true');
        }
    });

    var loadConfigPrefs = function() {
        if (localStorage.getItem("config_open") == 'true') {
            $('#configure').modal('show');
        }
    }
    loadConfigPrefs();


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
