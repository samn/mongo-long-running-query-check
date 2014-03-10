#! /usr/bin/env python
import json
from optparse import OptionParser
import subprocess
import sys

class MongoLongRunningQueryCheck():
    def __init__(self, options):
        self.host = options.host
        self.max_query_duration_seconds = options.max_query_duration_seconds
        self.output_indicator = 'Long Running Query Found:'

    def query_command(self):
        return """
        db.currentOp().inprog.forEach(
            function(op) {
                if(op.secs_running >= %(max_query_duration_seconds)s) {
                    print("%(output_indicator)s);
                    printjson(op);
                }
            }
        );
        """ % self.__dict__

    def get_long_running_queries(self):
        return subprocess.check_output(["mongo", "--host", self.host, "--eval", self.query_command()])

    def event_description(long_running_queries):
        return """
        Long Running Queries (longer than %(max_query_duration_seconds)s seconds) have been found.

        To kill a query:
        1. $ ssh this-mongodb-server
        2. $ mongo
        3. > db.killOp(opId)

        %(long_running_queries)s
        """ % {"max_query_duration_seconds": self.max_query_duration_seconds,
               "long_running_queries": long_running_queries}

    def construct_event(self, long_running_queries):
        event = {}
        event["service"] = "MongoDB Long Running Queries"
        event["state"] = "critical"
        event["metric"] = long_running_queries.count(self.output_indicator)
        event["description"] = self.event_description(long_running_queries)
        event["attributes"] = {}
        event["attributes"]["max_query_duration_seconds"] = self.max_query_duration_seconds
        return event

    def report_long_queries(self):
        long_queries_output = self.get_long_running_queries()
        if self.output_indicator in long_queries_output:
            event = construct_event(long_queries_output)
            print json.dumps(event)

if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("--host", default="localhost", help="The host of the database to monitor. (default=localhost)")
    parser.add_option("--max-query-duration-seconds", default=120, help="Queries that have been running for at least this many seconds will be reported (default = 120)")
    options, args = parser.parse_args()
    MongoLongRunningQueryCheck(options).report_long_queries()