import json
import logging
import os
import re

class ArticleNotFound(Exception):
    pass

class ArticleMetadataNotFound(Exception):
    pass

class Article():
    def __init__(self, filename):
        self.filename = filename
        self.title = None
        self.date = None

        if filename.endswith('.html') \
          and os.path.basename(filename) != 'index.html':

            logging.info('Found ' + filename)
            self.extract_title_and_date()
        else:
            raise ArticleNotFound()

        if self.title is None or self.date is None:
            raise ArticleMetadataNotFound()

    def extract_title_and_date(self):
        with open(self.filename) as file:
            for line in file:
                tm = re.search(r'<title>(.+)</title>', line)
                if tm:
                    self.title = tm.group(1)

                dm = re.search(r'<meta name="date.created" content="(.+)">', line)
                if dm:
                    self.date = dm.group(1)

                if '</head>' in line:
                    return

    def update(self, previous_article, next_article):
        return True

class ThreadNotFound(Exception):
    pass

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
            raise ThreadNotFound()

    def update(self):
        self.find_articles()
        self.articles.sort(key = lambda x: x.date)

        for index, article in enumerate(self.articles):
            article.update(self.article(index - 1), self.article(index + 1))

        self.make_index()

    def find_articles(self):
        self.articles = []
        for entry in os.scandir(self.directory):
            try:
                if entry.is_file():
                    self.articles.append(Article(entry.path))
            except ArticleNotFound:
                pass

    def article(self, index):
        if index >= 0 and index < len(self.articles):
            return self.articles[index]
        else:
            return None

    def make_index(self):
        return False

def find(directory):
    '''
    Look for sub-directories that contain a thread.

    Return a list of configured Thread objects.
    '''
    threads = []
    try:
        for entry in os.scandir(directory):
            if entry.is_dir():
                try:
                    threads.append(Thread(entry.path))
                except ThreadNotFound:
                    pass

    except FileNotFoundError:
            pass

    return threads

def index(thread_list):
    '''
    Create an index.html file showing all the threads in the list.
    '''
    pass
