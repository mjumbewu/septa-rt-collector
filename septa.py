import requests
import psycopg2
import redis
import logging

from urllib.parse import urlsplit

routes = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', '31', '32', '33', '34', '35', '36', '37', '38', '39', '40', '42', '43', '44', '46', '47', '47M', '48', '50', '52', '53', '54', '55', '56', '57', '58', '59', '60', '61', '62', '64', '65', '66', '67', '68', '70', '73', '75', '77', '78', '79', '80', '84', '88', '89', '90', '91', '92', '93', '94', '95', '96', '97', '98', '99', '101', '102', '103', '104', '105', '106', '107', '108', '109', '110', '111', '112', '113', '114', '115', '116', '117', '118', '119', '120', '123', '124', '125', '126', '127', '128', '129', '130', '131', '132', '133', '139', '150', '201', '204', '205', '206', '310', 'G', 'J', 'K', 'L', 'LUCY', 'R', 'H', 'XH']
urltmp = 'http://www3.septa.org/hackathon/TransitView/{}'
sqltmp = '''
    INSERT INTO measurements (route,data,measured_at)
    VALUES (%s,%s,%s)
'''

log = logging.getLogger(__name__)

def getdata(route):
    try:
        url = urltmp.format(route)
        response = requests.get(url)
        return response.text
    except Exception as exc:
        log = logging.getLogger(__name__)
        log.info('{} received while getting {}: "{}"'.format(type(exc).__name__, url, exc))
        return ''

def markvehicle(conn, id):
    hashstring = id.replace(' ', '').replace('"', '').replace(':', '').replace(',', '').strip('{}')
    log.debug('Hash string {}'.format(hashstring))
    return conn.set(hashstring, '', ex=1800, nx=True)

def savedata(cursor, route, vehicle, dt):
    log.debug('Saving {}, {}, {} to the database'.format(route, vehicle, dt.isoformat()))
    cursor.execute(sqltmp, (route, vehicle, dt.isoformat()))

def make_dbconn(url):
    log.info('Connecting to the database')
    return psycopg2.connect(url)

def make_dbcursor(conn):
    log.debug('Creating a database cursor')
    return conn.cursor()

def finish_dbcursor(conn, cursor):
    log.debug('Committing to the database')
    conn.commit()
    log.debug('Closing the cursor')
    cursor.close()

def make_redisconn(url):
    log.info('Connecting to the Redis server')
    scheme, netloc, path, query, fragment = urlsplit(url)
    path = path.strip('/')

    try:
        auth, loc = netloc.split('@')
    except ValueError:
        loc = netloc
        auth = ''

    try:
        username, password = auth.split(':')
    except ValueError:
        password = None

    try:
        host, port = loc.split(':')
    except ValueError:
        host = loc
        port = 6379

    if path == '':
        path = '0'

    return redis.StrictRedis(host=host, port=port, db=path, password=password)

