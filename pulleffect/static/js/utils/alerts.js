/* Copyright (C) 2014 Wesleyan University
* 
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
* 
*   http://www.apache.org/licenses/LICENSE-2.0
* 
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/

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

// Override function for displaying a single alert
// var displayAlerts = function(flashed) {
//     if (flashed.length == 0)
//         return;
//     var alertMessage = flashed[0][1];
//     var alertType = flashed[0][0];
//     var alert = $('<div class="alert alert-' + getAlertType([alertType]) + '"><button type="button" class="close" data-dismiss="alert" aria-hidden="true">&times;</button>' + alertMessage + '</div>')
//     .hide()
//     .delay(500)
//     .slideDown(500)
//     .delay(4000)
//     .slideUp(500, function() {
//         $(this).remove();
//     });
//     $('#alerts').append(alert);
    
// }