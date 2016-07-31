from __future__ import division
__author__ = 'chchen'

from collections import Counter
import argparse
import yaml
import re
import logging
import logging.handlers

# This is a sample log parser python code
#
# The log parser is only handle particular parse requests and historical data. I would like to add expansion
# function to the original requests and make it reusable in some other log file processing.
#
# date: 07/29/2016
# By: Chaofeng Chen
# contact: cchen1103@gmail.com

# init records
pat = '^.*?\[(.*?):.*?"(\S+).*"(.*?)"$'
records = []

def validate_record(rec):
    (date, method, agent) = rec
    (day, month, year) = date.split('/')
    if int(day) > 31 or int(day) <= 0 or \
        month not in ('Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'):
        return False
    if method not in ('GET', 'PUT', 'POST', 'HEAD', 'DELETE', 'CONNECT', 'OPTIONS'):
        return False
    return True

# get arguments and options
parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
                                 description=
"""Parse log files and generate reports

The log parser reads list of log files and parse the logs according to the yaml configuration file.
The report will be generated according to the yaml configuration file.
We are using yaml configuration for pattern match, information extraction and filtering. I think that
this is a more portable way to parse complex log format than fixed delimiter.

The yaml configuration file contains following attributes:

  bots: <pattern string>
        pattern string: strings that indicates the user-agent belongs to a bots
  
""")
parser.add_argument('logs', metavar='filename', type=str, nargs='+', help='list of log file names')
parser.add_argument('-c', '--conf', metavar='conf_file', type=str, help='yaml configuration file')
parser.add_argument('-l', '--log', metavar='logfile', type=str, help='log file of logparser.py')
args = parser.parse_args()

# set logging
#
# prefer using logger config file which is easier to manager logger format
# For this test, code the format in the code to reduce complexity
formatter = logging.Formatter("%(asctime)s %(name)s %(levelname)s \"%(message)s\"")
handler = logging.handlers.RotatingFileHandler(args.log, maxBytes=100000000, backupCount=9) \
    if args.log else logging.StreamHandler()
handler.setFormatter(formatter)
logger=logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(handler)

# read configuration file and parse the configuration
agent_os = {}
with open(args.conf) as c:
    try:
        agent_os = yaml.load(c)
    except:
        logger.error('Unable to parse configuration file %s' % args.conf)

# read through all logs files
for log in args.logs:
    try:
        with open(log) as logfile:
            lines = logfile.readlines()
    except:
        logger.error("Unable to read or parse log file %s" % log)
    
    # parse logs
    for line in lines:
        field = re.match(pat, line).groups()
        if field and validate_record(field):
            # parse os
            agent_attr = re.search('\((.*?)\)', field[2])
            if agent_attr:
                attributes = agent_attr.group(1).split(';')
                os = attributes[2].strip() if len(attributes) >2 else attributes[-1].strip()
                if any(map(lambda test_os: test_os in os, agent_os.get('bots'))):
                    os = 'misc'
            else:
                os = 'misc'
            records.append(field + (os,))

total_req_date = Counter([rec[0] for rec in records])

# calculate total request sorted by date. Python dict will not guarantee sequence of key and we want to
# sort it for easy reading
print '\nTotal requests by date:\n'
for date in sorted(total_req_date.keys()):
    print '{:<12}{:<20}'.format(date, total_req_date[date])

# sort and find the 3 most common agents by date
print '\nTop 3 common agents by date:\n'
for date in sorted(total_req_date.keys()):
    most_common_agent_by_date = Counter([rec[2] for rec in records if rec[0] == date]).most_common(3)
    for (agent, count) in most_common_agent_by_date:
        print '{:<12}{:<84}{:<12}'.format(date, agent, count)

# calculate the OS and method by date
print '\nGET/POST ratio by OS by date:\n'
for date in sorted(total_req_date.keys()):
    req_get_by_date = Counter(rec[3] for rec in records if rec[0] == date and rec[1] == 'GET')
    req_post_by_date = Counter(rec[3] for rec in records if rec[0] == date and rec[1] == 'POST')
    for os in set(req_get_by_date.keys()) | set(req_post_by_date.keys()):
        if req_post_by_date[os]:
            print '{:<12}{:<40}{:<12}'.format(date, os, req_get_by_date[os]/req_post_by_date[os])
        else:
            print '{:<12}{:<40}{:<12}'.format(date, os, 'infinity')
