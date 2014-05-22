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


dept_to_job_id_dict = {
    "cfa_lab": "4044",
    "has_lab": "2832",
    "keck_lab": "4045",
    "lang_lab": "4046",
    "olin_lab": "4047",
    "pac_lab": "4048",
    "st_lab": "4049",
    "special_projects": "272271",
    "om": "28203",
    "events": "4050",
    "grad": "35696",
    "tech": "4052",
    "temp": "2836",
    "temp_events": "66847",
    "training": "24502",
    "wes_pregame": "308306"
}
job_id_to_dept_dict = dict((v, k) for k, v in dept_to_job_id_dict.iteritems())


def get_job_id(dept, default):
    """Gets job id corresponding to given dept.

        Keyword arguments:
            dept -- dept map with job id
            default -- default job id to return when job id not found

        Returns:
            job id that maps to dept iff job id is in dept_to_job_id_dict
    """
    return dept_to_job_id_dict.get(dept, default)


def get_dept(job_id, default):
    """Gets dept corresponding to given job id.

        Keyword arguments:
            job_id -- job id to map with dept
            default -- default job id to return when dept not found

        Returns:
            dept that maps to job id iff dept is in job_id_to_dept_dict
    """
    return job_id_to_dept_dict.get(job_id, default)


def get_all_depts():
    """Gets all departments from dept_to_job_id_dict keys.
    """
    return dept_to_job_id_dict.keys()


def get_all_job_ids():
    """Gets all job ids from dept_to_job_id_dict values.
    """
    return dept_to_job_id_dict.values()
