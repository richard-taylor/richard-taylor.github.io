#!/usr/bin/python3

import logging
import os.path
import sys

directory = '.' if len(sys.argv) < 2 else sys.argv[1]

logging.basicConfig(format = '%(levelname)s:%(message)s', level = logging.INFO)
logging.info('Threading in %s', directory)

import threads
thread_list = threads.find(directory)

table = ''
for thread in thread_list:
    table = table + '<p>' + thread.config['name'] + '</p>\n'
        
f_template = os.path.join(directory, 'index.o.html')
f_index = f_template.replace('.o.', '.')

with open(f_index, 'w') as index:

    with open(f_template, 'r') as template:
        index.write(template.read().replace('__THREADS_INDEX__', table))
        
logging.info('Index %s', f_index)
