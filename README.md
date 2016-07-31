log_parser.py

This is a sample python script to parse web server log files.

This is a short and simplified log parser script to parse web server logs files and generate 3 reports:

    1. Total requests by date
    2. Most 3 frequent agents by date
    3. GET/POST ratio by OS by date

Due to the sample code and simplified requirements, the code is straight forward and no need to create unittest. Although
the simplified code, I still want to provide enough flexibility and portable for easy of use. Here are 2 features that
I introduced into the sample code:

    1. Allow to parse multiple logs instead of one in one line command.
    2. Allow to change regular expression match groups in configuration file instead of code change to match different
       log format
    3. Provide log and log rotate for log parser script
    4. Use OS pattern string to identify proper OS through user-agent with best effort

Installation:
    The script requires Python 2.x and PyYAML module. Install PyYAML module by
        pip install pyyaml
    Install the script
        git clone https://github.com/chaofeng/desk_com.git
    
    Modify parser_conf.yaml to meet your need.
    
Execution:
    
    Get command line help manual:
        
        python log_parser.py -h [--help]
        
    Parse web server logs and generate reports. If -l or --log is omitted, all logs will be direct to console.
    
        python log_parser.py [-c, --conf] parser_conf.yaml [[-l, --log] log_file]
    
    To view the log_parser log file:
        
        less <path to the log file>
         
Configuration Reference
    
    loglevel: ERROR
        - option of the following [DEBUG, INFO, WARNING, ERROR, NONE]. Set log_parser log level
    pattern: '^.*?\[(.*?):.*?"(\S+).*"(.*?)"$'
        - the regular expression to do group match and field extractions from log into desired fields
    os:
      - 'window'
      - 'mac'
      - 'solaris'
        
        - list of string pattern that used in user-agent to help identify os type. Using user-agent to identify os
          is not accurate and not recommend. This is the best guess effort.

Tests

This script has been tested under python 2.7.

Contributors

Chaofeng Chen (cchen1103@gmail.com)


License

This sample code can  be use, modify freely in all environments. There is no license restriction.