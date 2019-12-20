#!/usr/bin/python3

import logging
import os.path
import sys

directory = '.' if len(sys.argv) < 2 else sys.argv[1]

logging.basicConfig(format = '%(levelname)s:%(message)s', level = logging.INFO)
logging.info('Threading in %s', directory)

import threads
thread_list = threads.find(directory)

for thread in thread_list:
    thread.update()

threads.index(directory, thread_list)
threads.rss(directory, thread_list)
