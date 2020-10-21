#!/usr/bin/env python3
from __future__ import print_function

import os, sys, ipaddress
import re
import argparse
import errno
import logging

'''
To define a new area, use the following site to create a zip list
https://www.freemaptools.com/find-zip-codes-inside-user-defined-area.htm
'''

logger = logging.getLogger(__name__)

columbus_zip_codes=[20128,43001,43002,43003,43004,43007,43008,43009,43010,43011,43013,43015,43016,43017,43018,43021,43023,43025,43026,43027,43028,43029,43030,43031,43032,43033,43035,43036,43040,43041,43044,43045,43046,43047,43048,43050,43054,43055,43056,43058,43060,43061,43062,43064,43065,43066,43067,43068,43069,43073,43074,43076,43077,43078,43080,43081,43082,43084,43085,43086,43093,43102,43103,43105,43106,43109,43110,43112,43113,43115,43116,43117,43119,43123,43125,43126,43128,43130,43136,43137,43140,43143,43145,43146,43147,43148,43150,43151,43153,43154,43155,43156,43157,43162,43164,43194,43195,43199,43201,43202,43203,43204,43205,43206,43207,43209,43210,43211,43212,43213,43214,43215,43216,43217,43218,43219,43220,43221,43222,43223,43224,43226,43227,43228,43229,43230,43231,43232,43234,43235,43236,43240,43251,43260,43266,43268,43270,43271,43272,43279,43287,43291,43315,43319,43321,43334,43336,43338,43342,43344,43350,43351,43356,43528,43560,43613,43701,43830,43943,43952,43953,43977,45011,45044,45356,45368,45369,45459,45601,48076,96349]

cincy_zip_codes=[47023,47250,47034,47037,47042,40070,47036,47224,47006,41008,40050,47039,47017,47033,47024,40058,47021,47031,40011,40075,47030,47041,47043,47018,47011,41098,47032,41045,40007,40057,40363,41083,47012,47001,47022,40036,47019,47040,40355,47353,47020,47035,47025,47060,47016,41086,47038,41095,47003,47010,41080,40359,41046,45053,45033,45003,41052,45052,41091,41005,45030,45002,45063,45056,45001,41048,45041,41092,40379,41021,45275,45233,45248,41035,45247,45061,45013,41042,45051,41094,45252,41025,41022,45064,45004,41018,45238,45251,45211,41030,41097,45204,41054,41010,45205,45239,45014,41017,45012,45018,45062,45223,41051,45214,45225,41016,45231,45203,45224,45015,41011,40370,45220,45218,45240,45232,45055,45219,41014,41012,41019,41063,45217,45011,41072,45202,45229,45235,45206,41071,45067,41015,45254,45216,41073,45246,45207,41099,41074,45215,41033,45201,45221,45222,45234,45250,45253,45258,45262,45263,45264,45267,45268,45269,45270,45271,45273,45274,45277,45280,45296,45298,45299,45999,41053,45212,41075,45237,41076,45042,45208,45209,45213,45226,45069,45071,45236,41085,45241,41001,45230,45227,41003,45044,45050,45242,41040,45243,45255,41059,45249,41006,45244,45174,45005,45147,45040,41007,45111,45245,41031,45034,45140,45039,45150,45066,45157,45036,45156,45102,45065,45153,41061,41043,45103,45112,45160,45152,45122,41004,45120,45158,45162,45068,45054,41064,45106,45176,45032,45130,45119,45113,41002,45131,41044,45107,45118,41062,45154,45121,41034,45148,45114,41055,45177,41096,45167,45171,45146,45142,41056,45164,45168,45101,45155,45307,45115,45159,45166,45169,45697,45618,45105,45132,45144,43142,45133,45679,45135,41189,45693,45650,45172,45123,45624,45660,45646]

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
    other = []
    def city_matcher(row_data):
        try:
            member_num, renew_date, first_name, middle_name, last_name, company, address_1, address_2, city, state, mzip, country, email, home_phone, work_phone, mobile_phone, original_join_date = row_data
        except:
            try:
                mtype, member_number, paid_thru, autorenew, first_name, middle_name, last_name, company, address_1, address_2, city, state_province, mzip, country, home_phone, work_phone, mobile_phone, email, join_date, original_join_date, member_type, chapter, last_updated, bmw_model1, bmw_model1year, bmw_model2, bmw_model2year, primary_chapter, chapter2, chapter3, chapter4, chapter5, chapter6, chapter7, chapter8, chapter9, chapter10, identification_flag, numeric_member_number, account_number, referred_by, paid_thru_date, newsletter_preference, birth_dt = row_data
            except:
                print('Can\'t identify data, skipping {}'.format(row_data))
        if email:
            if mzip:
                simple_zip, *_ = mzip.split('-')
                if simple_zip.isdigit():
                    if int(simple_zip) in columbus_zip_codes:
                        columbus.append([first_name, last_name, email])
                    if int(simple_zip) in cincy_zip_codes:
                        cincy.append([first_name, last_name, email])
                    else:
                        if args.debug:
                            print([first_name, last_name, email])
                        other.append([first_name, last_name, email])
                else:
                    print('Non digit zip detected: {}'.format(simple_zip))
            else:
                print('No zip detected for email: {}'.format(email))
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
            if args.debug:
                print(row)
            member = city_matcher([cell.value for cell in row])
    elif extension in ['xls']:
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
        print('Unknown file extension: "{}"'.format(extension))

    if not args.city:
        print('#' * 50)
        print(f'----- Other -----')
        for member in other:
            print(','.join(member))
        print('#' * 50)
        print('*' * 50)
    if args.city == 'cbus' or not args.city:
        print(f'----- Columbus -----')
        for member in columbus:
            print(','.join(member))
        print('*' * 50)
    if args.city == 'cincy' or not args.city:
        print(f'----- Cincy -----')
        for member in cincy:
            print(','.join(member))
        print('*' * 50)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Used to distribute a larger membership file into smaller zip code regions')
    parser.add_argument('-f', '--xls_file', help='The file containing the member info')
    parser.add_argument('-c', '--city', help='filter by city, cbus or cincy')
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

