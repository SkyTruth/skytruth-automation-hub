
from logger import Logger
import testcasebase

class LoggerTest(testcasebase.AppEngineTestCase):
        
    def testlog(self):
        logger = Logger()
        result = logger.log (test='TEST')
        self.assertEqual(result['response'],'ok')
        
        
if __name__ == '__main__':
    unittest.main()        