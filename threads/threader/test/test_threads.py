
import threader.threads
import unittest

class TestThreads(unittest.TestCase):

    def test_valid(self):
        t = threader.threads.Thread('examples/t1')
        self.assertTrue(t is not None)
        self.assertTrue(t.valid())
        self.assertEqual('T1 name', t.config['name'])

    def test_invalid(self):
        t = threader.threads.Thread('examples/not-a-thread')
        self.assertTrue(t is not None)
        self.assertFalse(t.valid())
   
    def test_find(self):
        ts = threader.threads.find('examples')
        self.assertEqual(1, len(ts))
        
    def test_find_nothing(self):
        ts = threader.threads.find('not-examples')
        self.assertEqual(0, len(ts))
        
if __name__ == '__main__':
    unittest.main()
