import datetime
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
        self.description = None

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

                dm = re.search(r'<meta name="description" content="(.+)">', line)
                if dm:
                    self.description = dm.group(1)

                if '</head>' in line:
                    return

    def update(self, previous_article, next_article):

        previous = self.link(previous_article, 'This is the first article')
        next = self.link(next_article, 'This is the latest article')

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
        self.articles = []

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

    def count(self):
        return len(self.articles)

    def latest(self):
        return self.article(self.count() - 1)

    def make_index(self):
        filename = os.path.join(self.directory, 'index.html')

        header = '''<!DOCTYPE html>
<html lang="en">
<head>
<title>{0}</title>
<link rel="stylesheet" href="style.css">
</head>
<body>

<!-- GENERATED FILE -->

<h1 class="title">{0}</h1>
<a href="../contact.html">Richard Taylor</a>

'''
        with open(filename, 'w') as index:
            index.write(header.format(self.config['name']))

            if 'description' in self.config:
                index.write('<p>{}\n'.format(self.config['description']))

            index.write('<dl class="index">\n')

            for article in self.articles:
                link = '<a href="{0}">{1}</a>'.format(
                  os.path.basename(article.filename), article.title
                )
                index.write('<dt>{} {}</dt>\n'.format(article.date, link))

            index.write('</dl>\n')
            index.write('<div class="nav"><a href="../index.html">More threads...</a></div>\n')
            index.write('<p><a href="../rss.xml">RSS feed</a>\n')
            index.write('</body>\n</html>\n')

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

def index(directory, thread_list):
    '''
    Create an index.html file showing all the threads in the list.
    '''
    filename = os.path.join(directory, 'index.html')

    thread_list.sort(
        key = lambda x: x.latest().date if x.count() > 0 else '',
        reverse = True)

    header = '''<!DOCTYPE html>
<html lang="en">
<head>
<title>Threads</title>
<link rel="stylesheet" href="style.css">
</head>
<body>

<!-- GENERATED FILE -->

<h1 class="title">Threads</h1>
<a href="contact.html">Richard Taylor</a>

'''
    with open(filename, 'w') as index:
        index.write(header)

        index.write('<dl class="index">\n')

        for thread in thread_list:
            thread_index = '<a href="{0}/index.html">{1}</a>'.format(
                os.path.basename(thread.directory),
                thread.config['name']
            )
            count = thread.count()
            latest = thread.latest()
            title = latest.title if count > 0 else ''
            date = latest.date if count > 0 else ''

            if title != '':
                relative = os.path.relpath(latest.filename, directory)
                title = '<a href="{0}">{1}</a>'.format(relative, title)

            index.write('<dt>{}</dt>\n'.format(thread_index))
            index.write('<dd>{} {}</dd>\n'.format(date, title))

        index.write('</dl>\n')
        index.write('<p><a href="rss.xml">RSS feed</a>\n')
        index.write('</body>\n</html>\n')

def rss(directory, thread_list):
    '''
    Create an rss.xml file showing the 10 most recent thread articles.
    '''
    filename = os.path.join(directory, 'rss.xml')

    article_list = []
    for thread in thread_list:
        category = thread.config['name']
        for article in thread.articles:
            article.category = category
            article_list.append(article)

    article_list.sort(key = lambda x: x.date, reverse = True)
    last10 = article_list[0:10]

    header = '''<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
<channel>
<title>Richard Taylor's Threads</title>
<link>https://richard-taylor.github.io/threads/index.html</link>
<description>Series of articles by Richard Taylor BEng PhD</description>
<language>en</language>
'''
    base_url = 'https://richard-taylor.github.io/threads/'

    with open(filename, 'w') as rss:
        rss.write(header)

        iso8601 = '%Y-%m-%d'
        rfc822 = '%a, %d %b %Y 19:15:00 GMT'

        for article in last10:
            relative = os.path.relpath(article.filename, directory)
            link = base_url + relative

            date = datetime.datetime.strptime(article.date, iso8601)
            pub_date = date.strftime(rfc822)

            rss.write('<item>\n')
            rss.write('<title>{}</title>\n'.format(article.title))
            rss.write('<link>{}</link>\n'.format(link))

            if article.description is not None:
                rss.write('<description>{}</description>\n'.format(article.description))

            rss.write('<pubDate>{}</pubDate>\n'.format(pub_date))
            rss.write('<category>{}</category>\n'.format(article.category))
            rss.write('</item>\n')

        rss.write('</channel>\n</rss>\n')
