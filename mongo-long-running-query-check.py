#! /usr/bin/env python
import json
from optparse import OptionParser
import subprocess
import sys

class MongoLongRunningQueryCheck():
    def __init__(self, options):
        self.host = options.host
        self.max_query_duration_seconds = options.max_query_duration_seconds
        self.output_indicator = "Long Running Query Found:"
        self.username = options.username
        self.password = options.password

    def query_command(self):
        return """
        db.currentOp().inprog.forEach(
            function(op) {
                if (op.secs_running >= %(max_query_duration_seconds)s) {
                    print("%(output_indicator)s");
                    printjson(op);
                }
            }
        );
        """ % self.__dict__

    def get_long_running_queries(self):
        command = ["mongo", "--host", self.host, "--quiet", "--eval", self.query_command()]
        if self.username:
            command.extend(["--username", self.username])
        if self.password:
            command.extend(["--password", self.password])
        return subprocess.check_output(command)

    def event_description(long_running_queries):
        return """
        Long Running MongoDB Queries (longer than %(max_query_duration_seconds)s seconds)

        To kill a query:
        1. $ ssh this-mongodb-server
        2. $ mongo
        3. > db.killOp(opId)

        Queries running longer than %(max_query_duration_seconds)s seconds:
        %(long_running_queries)s
        """ % {"max_query_duration_seconds": self.max_query_duration_seconds,
               "long_running_queries": long_running_queries}

    def construct_event(self, long_running_queries):
        if self.output_indicator in long_queries_output:
            state = "critical"
        else:
            state = "ok"

        event = {}
        event["service"] = "MongoDB Long Running Queries"
        event["state"] = state
        event["metric"] = long_running_queries.count(self.output_indicator)
        event["description"] = self.event_description(long_running_queries)
        event["attributes"] = {}
        event["attributes"]["max_query_duration_seconds"] = self.max_query_duration_seconds
        return event

    def report_long_queries(self):
        long_queries_output = self.get_long_running_queries()
        event = construct_event(long_queries_output)
        print json.dumps([event])

if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("--host", default="localhost", help="The host of the database to monitor. (default=localhost)")
    parser.add_option("--max-query-duration-seconds", default=120, help="Queries that have been running for at least this many seconds will be reported (default = 120)")
    parser.add_option("--username", help="The username used to authenticate with mongo")
    parser.add_option("--password", help="The password used to authenticate with mongo")
    options, args = parser.parse_args()
    MongoLongRunningQueryCheck(options).report_long_queries()
