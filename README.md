## mongo-long-running-query-check

A monitor for long running MongoDB queries
meant to be used with [Riemann](https://github.com/aphyr/riemann)
and [riemann-sumd](https://github.com/bmhatfield/riemann-sumd).

### Usage

    Usage: mongo-long-running-query-check.py [options]

    Options:
    -h, --help            show this help message and exit
    --host=HOST           The host of the database to monitor.
                            (default=localhost)
    --max-query-duration-seconds=MAX_QUERY_DURATION_SECONDS
                            Queries that have been running for at least this many
                            seconds will be reported (default = 120)
    --username=USERNAME   The username used to authenticate with mongo
    --password=PASSWORD   The password used to authenticate with mongo


### riemann-sumd config

    service: 'mongo-long-running-query-check'
    arg: 'mongo-long-running-query-check.py'
    ttl: 350
    tags: ['notify', 'mongo-queries']
    type: 'json'
