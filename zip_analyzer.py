#!/usr/bin/env python3
from __future__ import print_function

import os, sys, ipaddress
import re
import argparse
import errno
import logging

'''
'''

logger = logging.getLogger(__name__)

columbus_zip_codes=[20128,
 43001,
 43002,
 43003,
 43004,
 43007,
 43008,
 43009,
 43010,
 43011,
 43013,
 43015,
 43016,
 43017,
 43018,
 43021,
 43023,
 43025,
 43026,
 43027,
 43028,
 43029,
 43030,
 43031,
 43032,
 43033,
 43035,
 43036,
 43040,
 43041,
 43044,
 43045,
 43046,
 43047,
 43048,
 43050,
 43054,
 43055,
 43056,
 43058,
 43060,
 43061,
 43062,
 43064,
 43065,
 43066,
 43067,
 43068,
 43069,
 43073,
 43074,
 43076,
 43077,
 43078,
 43080,
 43081,
 43082,
 43084,
 43085,
 43086,
 43093,
 43102,
 43103,
 43105,
 43106,
 43109,
 43110,
 43112,
 43113,
 43115,
 43116,
 43117,
 43119,
 43123,
 43125,
 43126,
 43128,
 43130,
 43136,
 43137,
 43140,
 43143,
 43145,
 43146,
 43147,
 43148,
 43150,
 43151,
 43153,
 43154,
 43155,
 43156,
 43157,
 43162,
 43164,
 43194,
 43195,
 43199,
 43201,
 43202,
 43203,
 43204,
 43205,
 43206,
 43207,
 43209,
 43210,
 43211,
 43212,
 43213,
 43214,
 43215,
 43216,
 43217,
 43218,
 43219,
 43220,
 43221,
 43222,
 43223,
 43224,
 43226,
 43227,
 43228,
 43229,
 43230,
 43231,
 43232,
 43234,
 43235,
 43236,
 43240,
 43251,
 43260,
 43266,
 43268,
 43270,
 43271,
 43272,
 43279,
 43287,
 43291,
 43315,
 43319,
 43321,
 43334,
 43336,
 43338,
 43342,
 43344,
 43350,
 43351,
 43356,
 43528,
 43560,
 43613,
 43701,
 43830,
 43943,
 43952,
 43953,
 43977,
 45011,
 45044,
 45356,
 45368,
 45369,
 45459,
 45601,
 48076,
 96349]


def setup_logging(verbosity):
    if verbosity > 2:
        log_level = logging.DEBUG
    elif verbosity > 1:
        log_level = logging.INFO
    elif verbosity:
        log_level = logging.WARNING
    else:
        log_level = logging.ERROR
    log_file = 'member_importer.log.txt'
            
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(name)s - %(message)s')
            
    l = logging.getLogger()
    l.setLevel(log_level)
    
    ch = logging.StreamHandler()
    ch.setLevel(log_level)
    ch.setFormatter(formatter)
    l.addHandler(ch)
    
    fh = logging.FileHandler(log_file)
    fh.setLevel(log_level)
    fh.setFormatter(formatter)
    l.addHandler(fh)


def main(args):
    columbus = []
    cincy = []
    dayton = []
    toledo = []
    def city_matcher(row_data):
        try:
            member_num, renew_date, first_name, middle_name, last_name, company, address_1, address_2, city, state, mzip, email, home_phone, work_phone, mobile_phone, original_join_date = row_data
        except:
            try:
                mtype, member_number, paid_thru, autorenew, first_name, middle_name, last_name, company, address_1, address_2, city, state_province, mzip, country, home_phone, work_phone, mobile_phone, email, join_date, original_join_date, member_type, chapter, last_updated, bmw_model1, bmw_model1year, bmw_model2, bmw_model2year, primary_chapter, chapter2, chapter3, chapter4, chapter5, chapter6, chapter7, chapter8, chapter9, chapter10, identification_flag, numeric_member_number, account_number, referred_by, paid_thru_date, newsletter_preference, birth_dt = row_data
            except:
                print('Can\'t identify data, skipping {}'.format(row_data))
        if email:
            simple_zip, *_ = mzip.split('-')
            if simple_zip.isdigit():
                if int(simple_zip) in columbus_zip_codes:
                    columbus.append([first_name, last_name, email])
                elif args.debug:
                    print([first_name, last_name, email])
        elif args.debug:
            print(f'No email for {first_name} {last_name}')

    if not args.xls_file:
        print('No file defined, exiting')
        sys.exit(1)
    xls_file = args.xls_file
    _, extension = xls_file.rsplit('.', 1)
    if extension in ['xlsx']:
        import openpyxl
        wb = openpyxl.load_workbook(xls_file)
        ws = wb.active
        for row in ws.iter_rows(min_row=2):
            member = city_matcher([cell.value for cell in row])
    if extension in ['xls']:
        import xlrd
        wb = xlrd.open_workbook(xls_file)
        ws = wb.sheet_by_index(0)
        # Skip the first row
        for rx in range(1,ws.nrows):
            member = city_matcher([cell.value for cell in ws.row(rx)])
    elif extension == 'csv':
        import csv
        with open(path) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            line_count = 0
            for row in csv_reader:
                member = city_matcher(row)
    else:
        print(f'Unknown file extension')

    print('*' * 50)
    for member in columbus:
        print(','.join(member))
    print('*' * 50)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Used to distribute a larger membership file into smaller zip code regions')
    parser.add_argument('-f', '--xls_file', help='The file containing the member info')
    parser.add_argument('-D', '--debug', help='Debug', action='store_true', default=False)
    parser.add_argument('-v', '--verbose', action='count', default=0)
    args = parser.parse_args()

    setup_logging(args.verbose)
    logger.debug('Starting')
    rc = 0
    try:
        rc = main(args)
    except Exception:
        logger.exception('Top lvl')
        rc = -1
    log_fn = logger.error if rc else logger.info
    log_fn('RC={}'.format(rc))
    sys.exit(rc)

