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

        previous = self.link(previous_article, 'This is the first article.')
        next = self.link(next_article, 'This is currently the latest article.')

        swaps = [
            Swap('<h1 class="title">{}</h1>', self.title),
            Swap('<span class="date_created">{}</span>', self.date),
            Swap('<span class="previous_article">{}</span>', previous),
            Swap('<span class="next_article">{}</span>', next)
        ]

        lines = []
        swapped = False
        with open(self.filename) as file:
            for line in file:
                for swap in swaps:
                    match = swap.pattern.search(line)
                    if match and match.group() != swap.substitution:
                        line = line.replace(match.group(), swap.substitution)
                        swapped = True
                lines.append(line)

        if swapped:
            with open(self.filename, 'w') as file:
                for line in lines:
                    file.write(line)

    def link(self, article, default_text):
        if article is None:
            return default_text
        return '<a href="{0}">{1}</a>'.format(
            os.path.basename(article.filename), article.title)

class Swap():
    def __init__(self, pattern, substitution):
        self.pattern = re.compile(pattern.replace('{}', '.*?'))
        self.substitution = pattern.replace('{}', substitution)

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
        filename = os.path.join(self.directory, 'index.html')

        header = '''<!DOCTYPE html>
<html>
<head>
<title>index of {0}</title>
<link rel="stylesheet" href="style.css"/>
</head>
<body>

<!-- GENERATED FILE -->

<h1 class="title">index of {0}</h1>
<a href="../contact.html">Richard Taylor</a>

'''

        with open(filename, 'w') as index:
            index.write(header.format(self.config['name']))

            if 'description' in self.config:
                index.write('<p>' + self.config['description'])

            index.write('<table class="index">\n')

            for article in reversed(self.articles):
                index.write('<tr>')
                index.write('<td>{}</td>'.format(article.title))
                index.write('<td>{}</td>'.format(article.date))
                index.write('</tr>\n')

            index.write('</table>\n</body>\n</html>')

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
