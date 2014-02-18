import unittest
from google.appengine.api import memcache
from google.appengine.ext import db
from google.appengine.ext import testbed
from google.appengine.api import taskqueue
import webtest
import base64
import json
import os

import pubsub
from pubsub import PubSub
from taskqueue import TaskQueue
import testcasebase 

class PubSubTest(testcasebase.AppEngineTestCase):

    def set_up(self):
        self.testapp = webtest.TestApp(pubsub.app)

    def testPubSub(self):
        sub_data = {'secret': 'SECRET'}
        id = PubSub.subscribe ('EVENT', 'not_an_url', sub_data)
        self.assertTrue (PubSub.unsubscribe (id))
        self.assertFalse (PubSub.unsubscribe (id))

        pub_data = {'message': 123}
        self.assertEqual(0, PubSub.publish ('EVENT', pub_data))
        PubSub.subscribe ('EVENT', 'not_an_url', sub_data)
        self.assertEqual(1, PubSub.publish ('EVENT', pub_data))
        response = self.executeTask() # /pubsub/notify
        self.assertEqual(response.status_int, 200)
        response.mustcontain ('unknown url type')
        
        url = "/pubsub/test" 
        PubSub.subscribe ('EVENT2', url, sub_data)
        self.assertEqual(1, PubSub.publish ('EVENT2', pub_data))
        response = self.executeTask()  # /pubsub/notify
        self.assertEqual (response.json['status'], 'OK')
        response = self.executeTask() # /pubsub/test
        self.assertEqual (response.json['pub_data']["message"], 123)

        url = "/pubsub/task" 
        sub_data = {'secret': 'SECRET', 'channel': 'CHANNEL', 'taskname': 'NAME'}
        PubSub.subscribe ('EVENT3', url, sub_data)
        self.assertEqual(1, PubSub.publish ('EVENT3', pub_data))
        response = self.executeTask()  # /pubsub/notify
        self.assertEqual (response.json['status'], 'OK')
        response = self.executeTask() # /pubsub/task
        self.assertEqual (response.json['status'], 'OK')
        queue = TaskQueue()
        lease = queue.lease (channel='CHANNEL')
        self.assertIsNotNone(lease)
        self.assertEqual(lease['id'], response.json['id'])
        

    def testTestHandler (self):
        params = {'some': 'data'}
        response = self.testapp.post_json('/pubsub/test', params)
        self.assertEqual(response.status_int, 200)
        self.assertEqual(params, response.json)
    
        
if __name__ == '__main__':
    unittest.main()        