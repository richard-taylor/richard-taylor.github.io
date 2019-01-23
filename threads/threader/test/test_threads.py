
import threader.test.help
import threader.threads
import os
import unittest

class TestThreads(unittest.TestCase):

    def test_valid(self):
        t = threader.threads.Thread('examples/t1')
        self.assertEqual('T1 name', t.config['name'])

    def test_invalid(self):
        try:
            threader.threads.Thread('examples/not-a-thread')
            self.fail()
        except threader.threads.ThreadNotFound:
            pass

    def test_find(self):
        ts = threader.threads.find('examples')
        self.assertEqual(1, len(ts))

    def test_find_nothing(self):
        ts = threader.threads.find('not-examples')
        self.assertEqual(0, len(ts))

    def test_update(self):
        index = 'examples/t1/index.html'
        try:
            t = threader.threads.Thread('examples/t1')
            t.update()
            self.assertEqual(2, len(t.articles))
            self.assertEqual('2018-12-31', t.articles[0].date)
            self.assertEqual('2019-01-01', t.articles[1].date)

            self.assertTrue(threader.test.help.find_in_file(
                index, 'T1 name')
            )
            self.assertTrue(threader.test.help.find_in_file(
                index, 'This thread is about something.')
            )
            self.assertTrue(threader.test.help.find_in_file(
                index, 'The Title')
            )
            self.assertTrue(threader.test.help.find_in_file(
                index, 'New Year')
            )
        finally:
            threader.test.help.quietly_remove(index)

    def test_valid_article(self):
        a = threader.threads.Article('examples/t1/small.html')
        self.assertEqual('The Title', a.title)
        self.assertEqual('2018-12-31', a.date)

    def test_bad_filenames(self):
        try:
            threader.threads.Article('examples/not-a-thread/file.txt')
            self.fail()
        except threader.threads.ArticleNotFound:
            pass

        try:
            threader.threads.Article('examples/t1/index.html')
            self.fail()
        except threader.threads.ArticleNotFound:
            pass

    def test_missing_title(self):
        try:
            threader.threads.Article('examples/not-a-thread/no-title.html')
            self.fail()
        except threader.threads.ArticleMetadataNotFound:
            pass

    def test_missing_date(self):
        try:
            threader.threads.Article('examples/not-a-thread/no-date.html')
            self.fail()
        except threader.threads.ArticleMetadataNotFound:
            pass

    def test_update_title_and_date(self):
        root = 'examples/not-a-thread/update'
        html = root + '.html'
        threader.test.help.copy_original(root)
        try:
            article = threader.threads.Article(html)
            article.update(None, None)

            self.assertTrue(threader.test.help.find_in_file(
                html, '<h1 class="title">DRY Title</h1>')
            )
            self.assertTrue(threader.test.help.find_in_file(
                html, '<span class="date_created">2018-11-11</span>')
            )
        finally:
            os.remove(html)

    def test_update_no_previous_or_next(self):
        root = 'examples/not-a-thread/middle'
        html = root + '.html'
        threader.test.help.copy_original(root)
        try:
            article = threader.threads.Article(html)
            article.update(None, None)

            self.assertTrue(threader.test.help.find_in_file(
                html, '<span class="previous_article">This is the first article.</span>')
            )
            self.assertTrue(threader.test.help.find_in_file(
                html, '<span class="next_article">This is currently the latest article.</span>')
            )
        finally:
            os.remove(html)

    def test_update_with_previous_and_next(self):
        root = 'examples/not-a-thread/middle'
        html = root + '.html'
        threader.test.help.copy_original(root)
        try:
            article = threader.threads.Article(html)
            prev = threader.threads.Article('examples/not-a-thread/previous-article.html')
            next = threader.threads.Article('examples/not-a-thread/next-article.html')

            article.update(prev, next)

            self.assertTrue(threader.test.help.find_in_file(
                html, '<span class="previous_article"><a href="previous-article.html">The Previous Article Title</a></span>')
            )
            self.assertTrue(threader.test.help.find_in_file(
                html, '<span class="next_article"><a href="next-article.html">The Next Article Title</a></span>')
            )
        finally:
            os.remove(html)

if __name__ == '__main__':
    unittest.main()
