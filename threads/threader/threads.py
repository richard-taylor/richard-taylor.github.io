import json
import logging
import os

class Thread():
    def __init__(self, directory):
        self.directory = directory
        self.config = None
        
        config_file = os.path.join(directory, 'thread.json')
        try:
            with open(config_file) as data:
                self.config = json.load(data)
                
            logging.info('Found thread named: ' + self.config['name'])
            
        except FileNotFoundError:
            pass
            
    def valid(self):
        return self.config is not None
        
def find(directory):
    '''
    Look for sub-directories that contain a thread.
    
    Return a list of configured Thread objects.
    '''
    threads = []
    try:
        for entry in os.scandir(directory):
            if entry.is_dir():
                thread = Thread(entry.path)
                if thread.valid():
                    threads.append(thread)
                    
    except FileNotFoundError:
            pass
               
    return threads
