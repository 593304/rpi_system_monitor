#!/usr/bin/env python3

import configparser
import json
import logging
import psutil
import psycopg2
import requests
import os

DRIVES = {
    'sd_card': '/',
    'nas': '/mnt/nas',
    'dev': '/mnt/dev',
    'cloud': '/mnt/cloud'
}

DB_CONNECTION = None
DB_CURSOR = None
TEMP_DB_FILE = '/mnt/dev/monitoring/RPI_data/temp_db'
FILE = None

LOGGER = None
LOG_FILE = '/mnt/dev/log/python/rpi_data_polling.log'
LOGGER_FORMAT = '%(asctime)15s | %(levelname)8s | %(name)s - %(funcName)12s - %(message)s'

CONFIG = None
CONFIG_FILE = '/mnt/dev/monitoring/RPI_data/get_rpi_data.conf'


def init():
    logging.basicConfig(filename=LOG_FILE, format=LOGGER_FORMAT, level=logging.INFO)
    global LOGGER
    LOGGER = logging.getLogger('polling_rpi_system')
    try:
        global DB_CONNECTION
        DB_CONNECTION = psycopg2.connect('dbname=adam user=adam')
        global DB_CURSOR
        DB_CURSOR = DB_CONNECTION.cursor()
        LOGGER.debug('Connected to the database')
        LOGGER.debug('Checking temp file')
        check_temp_file()
    except Exception:
        LOGGER.error('Cannot connect to the database, using the temporary file')
        global FILE
        FILE = open(TEMP_DB_FILE, 'a+')

    CONFIG = configparser.ConfigParser()
    CONFIG.read(CONFIG_FILE)


def check_temp_file():
    try:
        file = open(TEMP_DB_FILE, 'r')
        lines = file.readlines()
        LOGGER.info('Found temporary file with {} records'.format(len(lines)))
        file.close()
        for line in lines:
            save_to_db(json.loads(line))
        os.remove(TEMP_DB_FILE)
    except Exception:
        pass


def save_to_file(data):
    LOGGER.debug('Saving to file')
    FILE.write(json.dumps(data) + '\n')


def save_to_db(data):
    LOGGER.debug('Saving to DB ')
    DB_CURSOR.execute(
        'INSERT INTO '
        '  monitoring.rpi_data('
        '    cpu_temp_celsius, cpu0_usage_percent, cpu1_usage_percent, cpu2_usage_percent, cpu3_usage_percent, '
        '    mem_usage_mb, mem_total_mb, '
        '    sd_card_usage_gb, sd_card_total_gb, '
        '    nas_usage_gb, nas_total_gb, '
        '    dev_usage_gb, dev_total_gb, '
        '    cloud_usage_gb, cloud_total_gb, '
        '    timestamp) '
        'VALUES('
        '  %s, %s, %s, %s, %s, '
        '  %s, %s, '
        '  %s, %s, '
        '  %s, %s, '
        '  %s, %s, '
        '  %s, %s, '
        '  now());',
        (data['cpu_temp'], data['cpu_0_usage'], data['cpu_1_usage'], data['cpu_2_usage'], data['cpu_3_usage'],
         data['mem_usage'], data['mem_total'],
         data['disk_usage'], data['disk_total'],
         data['nas_usage'], data['nas_total'],
         data['dev_usage'], data['dev_total'],
         data['cloud_usage'], data['cloud_total']))
    DB_CONNECTION.commit()


def to_mb(in_bytes):
    return in_bytes / 1024 / 1024


def to_gb(in_bytes):
    return in_bytes / 1024 / 1024 / 1024


def main():
    # RPI Dashboard URL
    protocol = CONFIG.get('SERVER', 'PROTOCOL')
    host = CONFIG.get('SERVER', 'HOST')
    port = CONFIG.get('SERVER', 'PORT')
    path = CONFIG.get('SERVER', 'PATH')
    base_url = "{0}://{1}:{2}/{3}".format(protocol, host, port, path)

    # Getting the values in the beginning and in the end to get the average of them
    cpu_temp = psutil.sensors_temperatures()['cpu-thermal'][0].current
    mem_usage = to_mb(psutil.virtual_memory().used)
    disk_usage = to_gb(psutil.disk_usage(DRIVES['sd_card']).used)
    nas_usage = to_gb(psutil.disk_usage(DRIVES['nas']).used)
    dev_usage = to_gb(psutil.disk_usage(DRIVES['dev']).used)
    cloud_usage = to_gb(psutil.disk_usage(DRIVES['cloud']).used)

    # Getting the percents first, because it takes multiple seconds to gather the information
    cpu_percents = psutil.cpu_percent(interval=15, percpu=True)
    cpu_0_usage = cpu_percents[0]
    cpu_1_usage = cpu_percents[1]
    cpu_2_usage = cpu_percents[2]
    cpu_3_usage = cpu_percents[3]

    # Calculating the values
    cpu_temp = (psutil.sensors_temperatures()['cpu-thermal'][0].current + cpu_temp) / 2
    mem_usage = (to_mb(psutil.virtual_memory().used) + mem_usage) / 2
    mem_total = to_mb(psutil.virtual_memory().total)
    disk_usage = (to_gb(psutil.disk_usage(DRIVES['sd_card']).used) + disk_usage) / 2
    disk_total = to_gb(psutil.disk_usage(DRIVES['sd_card']).total)
    nas_usage = (to_gb(psutil.disk_usage(DRIVES['nas']).used) + nas_usage) / 2
    nas_total = to_gb(psutil.disk_usage(DRIVES['nas']).total)
    dev_usage = (to_gb(psutil.disk_usage(DRIVES['dev']).used) + dev_usage) / 2
    dev_total = to_gb(psutil.disk_usage(DRIVES['dev']).total)
    cloud_usage = (to_gb(psutil.disk_usage(DRIVES['cloud']).used) + cloud_usage) / 2
    cloud_total = to_gb(psutil.disk_usage(DRIVES['cloud']).total)

    data = {
        'cpu_temp': cpu_temp,
        'cpu_0_usage': cpu_0_usage, 'cpu_1_usage': cpu_1_usage, 'cpu_2_usage': cpu_2_usage, 'cpu_3_usage': cpu_3_usage,
        'mem_usage': mem_usage, 'mem_total': mem_total,
        'disk_usage': disk_usage, 'disk_total': disk_total,
        'nas_usage': nas_usage, 'nas_total': nas_total,
        'dev_usage': dev_usage, 'dev_total': dev_total,
        'cloud_usage': cloud_usage, 'cloud_total': cloud_total}

    LOGGER.debug('RPI data: {}'.format(data))

    # Sending data to the REST APIs
    cpu_usage_path = CONFIG.get('SERVER', 'CPU_USAGE')
    cpu_usage_data = {
        'core0': cpu_0_usage,
        'core1': cpu_1_usage,
        'core2': cpu_2_usage,
        'core3': cpu_3_usage
    }
    try:
        requests.post("{0}/{1}".format(base_url, cpu_usage_path), json=cpu_usage_data)
    except Exception as e:
        LOGGER.error(str(e))

    cpu_temp_path = CONFIG.get('SERVER', 'CPU_TEMP')
    cpu_temp_data = {
        'temp': cpu_temp,
        'limit': 85.0
    }
    try:
        requests.post("{0}/{1}".format(base_url, cpu_temp_path), json=cpu_temp_data)
    except Exception as e:
        LOGGER.error(str(e))

    mem_usage_path = CONFIG.get('SERVER', 'MEM_USAGE')
    mem_usage_data = {
        'usage': mem_usage,
        'total': mem_total
    }
    try:
        requests.post("{0}/{1}".format(base_url, mem_usage_path), json=mem_usage_data)
    except Exception as e:
        LOGGER.error(str(e))

    disk_usage_path = CONFIG.get('SERVER', 'DISK_USAGE')
    disk_usage_data = {
        'sdUsage': disk_usage,
        'sdTotal': disk_total,
        'nasUsage': nas_usage,
        'nasTotal': nas_total,
        'devUsage': dev_usage,
        'devTotal': dev_total,
        'cloudUsage': cloud_usage,
        'cloudTotal': cloud_total
    }
    try:
        requests.post("{0}/{1}".format(base_url, disk_usage_path), json=disk_usage_data)
    except Exception as e:
        LOGGER.error(str(e))

    # Saving data
    if DB_CONNECTION is None:
        save_to_file(data)
        FILE.close()
    else:
        save_to_db(data)
        DB_CURSOR.close()
        DB_CONNECTION.close()


if __name__ == '__main__':
    init()
    main()
