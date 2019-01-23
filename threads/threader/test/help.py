
# helper functions for unit tests

import shutil

def copy_original(rootname):
    shutil.copyfile(rootname + '.original', rootname + '.html')

def find_in_file(filename, text):
    with open(filename, 'r') as file:
        for line in file:
            if text in line:
                return True
    return False
