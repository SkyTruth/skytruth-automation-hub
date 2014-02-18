from google.appengine.api import memcache
from google.appengine.ext import db
from google.appengine.ext import testbed

from seqid import SeqidManager

import testcasebase 


class SeqidTest(testcasebase.AppEngineTestCase):
        
    def testSeqidManager(self):
        mgr = SeqidManager ()
        seqid1 = mgr.issueSeqids('A')
        seqid2 = mgr.issueSeqids('A')
        self.assertTrue(seqid2 > seqid1)
        
        seqids = mgr.issueSeqids('B', 10)
        self.assertEqual(10, len(seqids))
        
        
        
        
if __name__ == '__main__':
    unittest.main()        