
import threader.threads
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
        t = threader.threads.Thread('examples/t1')
        t.update()
        self.assertEqual(2, len(t.articles))
        self.assertEqual('2018-12-31', t.articles[0].date)
        self.assertEqual('2019-01-01', t.articles[1].date)

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

if __name__ == '__main__':
    unittest.main()
