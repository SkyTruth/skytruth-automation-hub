# -*- coding: utf-8 -*-
import unittest2
import json
import apiclient.discovery


class TestTaskQueueAPI(unittest2.TestCase):
    """TaskQueue API test cases."""
    
    def setUp(self):
        self.service = apiclient.discovery.build("taskqueue", "v1.0", 
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
        
    def test_add (self):
        response = self.service.add(body=dict(channel='A', name='N', content='CONTENT')).execute()
        self.assertEqual(response['status'], 'OK')

        response = self.service.add(body={'channel': 'A', 'name': 'N', 'content': '{"abc":123}'}).execute()
        self.assertEqual(response['status'], 'OK')

        #Test missing Name field (required)
        try:
            response = self.service.add(body={'channel': 'A'}).execute()
        except Exception, err:
            response = str(err)
        self.assertEqual(response.find('Message AddTaskRequest is missing required field name') > 0, True)
            
        #TODO: Test invalid fields and data types

    def test_lease (self):
        content = {'abc': 123}
        response = self.service.add(body={'channel': 'L', 'name': 'N', 'content':json.dumps(content)}).execute()
        lease = self.service.lease(body={'channel': 'L', 'lease_seconds': 100}).execute()
        self.assertEqual(lease['status'], 'OK')
        self.assertEqual(lease['task']['channel'], 'L')
        self.assertEqual(lease['task']['name'], 'N')
        self.assertEqual(json.loads(lease['task']['content'])['abc'], 123)
        response = self.service.delete(body={'task_result': 'DONE', 'lease': lease}).execute()
        
        response = self.service.lease(body={'channel': 'DOES NOT EXIST', 'lease_seconds': 100}).execute()
        self.assertEqual(response['status'], 'NOT FOUND')
        
        
    def test_delete (self):
        response = self.service.add(body={'channel': 'D', 'name': 'N', 'content': 'CONTENT'}).execute()
        lease = self.service.lease(body={'channel': 'D', 'lease_seconds': 100}).execute()
        response = self.service.delete(body={'task_result': 'DONE', 'lease': lease}).execute()
        self.assertEqual(response['status'], 'OK')
    
        # try to delete the same task again
        response = self.service.delete(body={'task_result': 'DONE', 'lease': lease}).execute()
        self.assertEqual(response['status'], 'NOT FOUND')

        
if __name__ == '__main__':
    unittest.main()