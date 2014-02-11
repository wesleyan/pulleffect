
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