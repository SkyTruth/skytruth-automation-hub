# -*- coding: utf-8 -*-
import unittest2
import apiclient.discovery
import json


class TestGeoFeedAPI(unittest2.TestCase):
    """GeoFeed API test cases."""
    
    def setUp(self):
#        self.testapp = TestApp('http://localhost:8080#requests')
        self.service = apiclient.discovery.build("geofeed", "v1.0", 
                             discoveryServiceUrl=("http://localhost:8080/_ah/api/discovery/v1/"
                                                  "apis/{api}/{apiVersion}/rest"))

        self.geofeed = self.service
        
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
        
    def test_seqid (self):
        response = self.geofeed.seqid(series='topic').execute()
        self.assertEqual(response['status'], 'OK')
        self.assertEqual(response['series'], 'topic')
        seqid1 = response['seqid_int']
        response = self.geofeed.seqid(series='topic').execute()
        seqid2 = response['seqid_int']
        self.assertTrue(seqid2 > seqid1)

    def test_publish (self):
        item = {'topic': 'TOPIC', 'key': 'KEY'}
        response = self.geofeed.publish(body=item).execute()
        self.assertEqual(response['status'], 'OK')
 
    def test_list (self):
        # empty list
        response = self.geofeed.list(body={'topic':'LIST_TEST'}).execute()
        self.assertEqual(response['status'], 'OK')
        
        # add some items
        item = {'topic': 'LIST_TEST', 'key': '1'}
        response = self.geofeed.publish(body=item).execute()
        item = {'topic': 'LIST_TEST', 'key': '2'}
        response = self.geofeed.publish(body=item).execute()
        item = {'topic': 'LIST_TEST', 'key': '3'}
        response = self.geofeed.publish(body=item).execute()
    
        # now we should have a list
        response = self.geofeed.list(body={'topic':'LIST_TEST'}).execute()
        self.assertEqual(response['status'], 'OK')
        self.assertEqual(len(response['items']), 3)

    def test_get (self):
        # not found
        response = self.geofeed.get(body={'topic':'GET_TEST', 'key':'NOT_FOUND'}).execute()
        self.assertEqual(response['status'], 'NOT FOUND')
                   
        item = {'topic': 'GET_TEST', 'key': '1'}
        response = self.geofeed.publish(body=item).execute()
        item = {'topic': 'GET_TEST', 'key': '2'}
        response = self.geofeed.publish(body=item).execute()
        item = {'topic': 'GET_TEST', 'key': '3'}
        response = self.geofeed.publish(body=item).execute()
        
        #found
        response = self.geofeed.get(body={'topic':'GET_TEST', 'key':'2'}).execute()
        self.assertEqual(response['status'], 'OK')
        self.assertEqual(response['item']['key'], '2')

    def test_test (self):
        response = self.geofeed.test(body=dict(message='TEST')).execute()
        self.assertEqual(response['status'], 'OK')
        self.assertEqual(response['message'], 'TEST')
    
        
if __name__ == '__main__':
    unittest.main()