# -*- coding: utf-8 -*-
import unittest2
import apiclient.discovery
import json


class TestTestAPI(unittest2.TestCase):
    """Test API test cases."""
    
    def setUp(self):
        self.service = apiclient.discovery.build("test", "v1.0", 
                             discoveryServiceUrl=("http://localhost:8080/_ah/api/discovery/v1/"
                                                  "apis/{api}/{apiVersion}/rest"))

        
        # We should be able to do this wihtout running an external dev server.   However, something is broken in the 
        # endpoints initialization when running inside TestApp so that all requests return 404, as described here:
        #
        # http://stackoverflow.com/questions/20384743/how-to-unit-test-google-cloud-endpoints    
        #
        # If it worked, we could do this instead:
        #                
        # from taskqueue_api import app 
        # self.test_app = TestApp(app)
        #
        

    def test_test (self):
        response = self.service.test(body=dict(message='TEST')).execute()
        self.assertEqual(response['status'], 'OK')
        self.assertEqual(response['message'], 'TEST')
    
        
if __name__ == '__main__':
    unittest.main()