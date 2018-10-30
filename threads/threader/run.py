#!/usr/bin/python3

import logging
import sys

directory = '.' if len(sys.argv) < 2 else sys.argv[1]

logging.basicConfig(format = '%(levelname)s:%(message)s', level = logging.INFO)
logging.info('Threading in directory "%s"', directory)
