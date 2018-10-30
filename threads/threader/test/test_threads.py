
import threader.threads
import unittest

class TestThreads(unittest.TestCase):

    def test_init(self):
        t = threader.threads.Thread()
        self.assertTrue(t is not None)

if __name__ == '__main__':
    unittest.main()
