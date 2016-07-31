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
largest_N = 3   # number of most common agents want to show
records = []

def parse_record(data, pattern):
    """
    parse a string using regular expression and return the captured portion
    :param data: string of data/log need to be parsed
    :param pattern: regular expression. using () to capture match group
    :return: on success of finding matched group, a tuple of matched group content will be returned, otherwise,
        'None' will be returned
    """
    parse_data = re.search(pattern, data)
    if parse_data:
        rec = parse_data.groups()
        logger.debug('parse %s: %s' % (data, rec))
    else:
        logger.warn('record %s' % data)
        return
    return rec

def map_agent_to_os(agent, pattern):
    """
    best effort to map user-agent to OS.
    Using user-agent information to identify OS is not accurate.
    The user-agent can be easily comprised or deliberately modified.
    
    I am using a list of OS pattern to identify most likely OS type by user-agent.
    Select the one match os pattern as well as with longer information string
    :param agent: user-agent string
    :param pattern: list of OS pattern could be used in user-agent
    :return: OS information if found, otherwise empty string
    """
    os = ''
    os_info = re.search('\((.*?)\)', agent)
    if os_info:
        fields = os_info.group(1).split(';')
        # this is best effort to identify the OS from user-agent and it is not accurate
        # the user-agent can also been comprised or deliberately modified.
        # We are using a list try to filter out bots, spider, crawler and feeds and identify
        # most likely OS through user-agent.
        #
        # select the one match os pattern and with the longest field as the OS
        for field in fields:
            if any(map(lambda t: t in field.lower(), pattern)):
                os = max([os, field.strip()], key=len)
    return os

if __name__ == '__main__':
    # main program starts here
    # get arguments and options
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
                                     description=
    """Parse log files and generate reports
    
    The script reads list of log files and parses the logs according to the yaml configuration file.
    Three reports will be generated:
        total request by date
        most frequent agents by date
        GET to POST ratio by OS by date
    
    We are using yaml configuration for pattern match and fields extraction. There is no need to make code change rather
    than change in configuration file to fit different log format.
    
    The configuration file uses yaml format and requires following attributes:
    
      pattern: <string of regexpr>           # match groups to extract fields from logs
      bots: <array of pattern string>        # strings that identify bot user-agent
      
    """)
    parser.add_argument('logs', metavar='filename', type=str, nargs='+', help='list of log file names')
    parser.add_argument('-c', '--conf', metavar='conf_file', type=str, required=True, help='yaml configuration file')
    parser.add_argument('-l', '--log', metavar='logfile', type=str, help='log file of log_parser.py')
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
    with open(args.conf) as c:
        try:
            conf = yaml.load(c)
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
        records = [parse_record(line, conf['pattern']) for line in lines]
        # remove None records that failed in parsing
        records = filter(None, records)
    
    # calculate total request sorted by date. Python dict will not guarantee sequence of key and we want to
    # sort it for easy reading
    total_req_by_date = Counter([rec[0] for rec in records])
    print '\nTotal requests by date:\n'
    for date in sorted(total_req_by_date.keys()):
        print '{:<12}{:< 8}'.format(date, total_req_by_date[date])
    
    # sort and find the 3 most common agents by date
    print '\nTop %s common agents by date:\n' %largest_N
    for date in sorted(total_req_by_date.keys()):
        most_common_agent_by_date = Counter([rec[2] for rec in records if rec[0] == date]).most_common(largest_N)
        for (agent, count) in most_common_agent_by_date:
            print '{:<12}{:<84}{:< 8}'.format(date, agent, count)
    
    # calculate the OS and method by date
    print '\nGET/POST ratio by OS by date:\n'
    for date in sorted(total_req_by_date.keys()):
        req_get_by_date = Counter(map_agent_to_os(rec[2], conf['os'])
                                  for rec in records if rec[0] == date and rec[1] == 'GET')
        req_post_by_date = Counter(map_agent_to_os(rec[2],conf['os'])
                                   for rec in records if rec[0] == date and rec[1] == 'POST')
        # check agents that using either GET or POST or both methods
        for os in set(req_get_by_date.keys()) | set(req_post_by_date.keys()):
            if req_post_by_date[os]:
                print '{:<12}{:<40}{:< 8}'.format(date, os, req_get_by_date[os]/req_post_by_date[os])
            else:
                print '{:<12}{:<40}{:<8}'.format(date, os, ' infinity')