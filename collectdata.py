#!/usr/bin/env python

import json
import pytz
import os
import septa
import click
import logging
import logging.config

from datetime import datetime
from itertools import cycle
from time import sleep

log = logging.getLogger()
est = pytz.timezone('US/Eastern')

dburl = os.environ.get('DATABASE_URL')
redisurl = os.environ.get('REDIS_URL')

def collectroutes(dbconn, redisconn):
    for route in cycle(septa.routes):
        routestring = septa.getdata(route)
        timestamp = datetime.now().replace(tzinfo=est)

        if routestring == '':
            log.warning('Empty route string for route {}'.format(route))
            continue

        routedata = json.loads(routestring)
        totalcount = newcount = 0
        dbcursor = septa.make_dbcursor(dbconn)

        for vehicledata in routedata['bus']:
            vehiclestring = json.dumps(vehicledata)

            vehicledata.pop('Offset')
            idstring = json.dumps(vehicledata, sort_keys=True)

            if septa.markvehicle(redisconn, idstring):
                septa.savedata(dbcursor, route, vehiclestring, timestamp)
                newcount += 1
            totalcount += 1

        septa.finish_dbcursor(dbconn, dbcursor)
        log.info('found {} vehicles, {} new measurements for route {}'.format(totalcount, newcount, route))
        sleep(0.5)

@click.command()
@click.option('--loglevel', default='INFO', help='set the logging level')
def main(loglevel):
    # logging.basicConfig(
    #     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    #     level=getattr(logging, loglevel))
    logging.config.dictConfig({
        'version': 1,
        'disable_existing_loggers': False,
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'level': loglevel,
                'formatter': 'simple',
            },
            'null': {
                'class': 'logging.NullHandler',
            },
        },
        'formatters': {
            'simple': {
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            },
        },
        'loggers': {
            '': {
                'handlers': ['console'],
                'level': 'DEBUG',
            },
            'requests': {
                'handlers': ['console'],
                'level': 'WARNING'
            },
        },
    })
    # log.setLevel(loglevel)

    dbconn = septa.make_dbconn(dburl)
    redisconn = septa.make_redisconn(redisurl)

    try:
        collectroutes(dbconn, redisconn)
    except KeyboardInterrupt:
        print('Closing database connection.')
        dbconn.rollback()
        dbconn.close()

if __name__ == '__main__':
    try:
        main()
    except (SystemExit, KeyboardInterrupt):
        raise
    except Exception as e:
        log.error('Caught an exception', exc_info=True)
