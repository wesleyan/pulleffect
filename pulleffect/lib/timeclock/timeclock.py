# Copyright (C) 2014 Wesleyan University
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from flask import Blueprint
from flask import jsonify
from flask import request
from flask import make_response
from pulleffect.lib.utilities import require_signin
import pulleffect.lib.timeclock.timeclock_helper as tc_helper
import pulleffect.lib.timeclock.timeclock_objects as tc_obj


timeclock = Blueprint('timeclock', __name__, template_folder='templates')


@timeclock.route('')
@require_signin
def index():
    """Tries to get timeclock entries from Oracle db

    Returns: An array of timeclock entries of the form:

    Example Response:

            [{
                'username': 'aburkart',
                'dept': 'om',
                'time_in': <timestamp>,
                'time_out': <timestamp>
            }]

        or

            {
                'error' <some indicative error message>
            }


    Example route: 'http://localhost:3000/timeclock?username=aburkart'
    """
    # Get parsed Oracle timeclock request
    timeclockRequest = tc_helper.parse_request(request)

    # If timeclock request has errors, return them to the user
    if len(timeclockRequest.error_message) > 0:
        return make_response(jsonify(timeclockRequest.error_message), 400)

    # Build an oracle query from the request
    timeclockOracleQuery = tc_obj.TimeclockOracleQuery(
        timeclockRequest.username, timeclockRequest.time_in,
        timeclockRequest.time_out, timeclockRequest.job_ids,
        timeclockRequest.limit)

    # Try to get the timeclock entries
    tc_entries = tc_helper.try_get_timeclock_entries(timeclockOracleQuery)

    # Fetches timeclock entries from Oracle db
    return jsonify(tc_entries)
