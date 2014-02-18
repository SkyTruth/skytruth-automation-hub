from google.appengine.api import memcache
from google.appengine.ext import db
from google.appengine.ext import testbed
import webtest
import time 

from geofeed import GeoFeed
import geofeed
from pubsub import PubSub
import pubsub
from taskqueue import TaskQueue
import testcasebase 


class GeoFeedTest(testcasebase.AppEngineTestCase):

    def set_up(self):
        self.testapp = webtest.TestApp(pubsub.app)
        self.geofeedapp = webtest.TestApp(geofeed.app)
        
    def testGeoFeed(self):
        item = {
            'topic': 'T',
            'key': 'K',
            'latitude': 39,
            'longitude': -79
        }
        id = GeoFeed.publish(**item)
        self.assertEqual(id, item['key'])
        time.sleep(2)
        item['key'] = 'L' 
        id = GeoFeed.publish(**item)
        self.assertEqual(id, item['key'])
    
        last_published = '9999'
        for doc in GeoFeed.list(item['topic']):
            self.assertLess(doc['published'], last_published)
            last_published = doc['published']
        
        for doc in GeoFeed.list('NOT_FOUND'):
            self.assertFalse('Should never get here')        
        
        doc = GeoFeed.get(item['topic'], item['key'])
        self.assertIsNotNone(doc)
        
        #set up PubSub subscription so that a task is created when an item is published to the feed
        sub_url = "/pubsub/task" 
        event=GeoFeed._indexname(item['topic'])
        channel='ProcessNew%s' % item['topic']
        sub_data = {'secret': 'SECRET', 'channel': channel, 'pubname': 'key'}
        PubSub.subscribe (event, sub_url, sub_data)
        
        # now publish a new item to the feed.  This should trigger creation of a new task in the queue
        id = GeoFeed.publish(**item)
        
        # need to manually process the task queue because we're in test mode
        response = self.executeTask()  # /pubsub/notify
        self.assertEqual (response.json['status'], 'OK')
        response = self.executeTask() # /pubsub/task
        self.assertEqual (response.json['status'], 'OK')
        
        # Now make sure there is a task in the queue
        queue = TaskQueue()
        lease = queue.lease (channel=channel)
        self.assertIsNotNone(lease)
        self.assertEqual(lease['id'], response.json['id'])
        self.assertEqual(lease['content']['pub_data']['key'], item['key'])

    def testHandler (self):
        response = self.geofeedapp.get('/geofeed/HANDLER_TEST/ITEM_KEY')
        self.assertEqual(response.status_int, 200)
        self.assertEqual(response.json['status'], 'NOT FOUND')
        item = {
            'topic': 'HANDLER_TEST',
            'key': 'ITEM_KEY',
            'latitude': 39,
            'longitude': -79
        }
        id = GeoFeed.publish(**item)
        self.assertEqual(id, item['key'])
        response = self.geofeedapp.get('/geofeed/HANDLER_TEST/ITEM_KEY')
        self.assertEqual(response.status_int, 200)
        self.assertEqual(response.json['status'], 'OK')
        self.assertEqual(response.json['item']['key'], 'ITEM_KEY')
        item['key'] = 'ITEM_KEY_2'
        id = GeoFeed.publish(**item)

        time.sleep(2)
        item['key'] = 'ITEM_KEY_3'
        id = GeoFeed.publish(**item)
        
        response = self.geofeedapp.get('/geofeed/HANDLER_TEST')
        # last item added should be first
        self.assertEqual(response.json[0]['key'], item['key'])
                        
if __name__ == '__main__':
    unittest.main()        