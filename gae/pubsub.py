"""
    Publish/Subscribe tool
    @author Paul Woods <paul@skytruth.org>
"""
import webapp2
from google.appengine.ext import db
from google.appengine.api import taskqueue
import json
import urllib2
import os
from taskqueue import TaskQueue


class Subscription (db.Model):
    event = db.StringProperty()
    url = db.StringProperty()
    created = db.DateTimeProperty(auto_now_add=True)
    data = db.StringProperty() #this contains arbitrary content encoded as json
    
class PubSub ():
    @staticmethod
    def publish (event, pub_data = None):
        """Publish an event.  This will trigger all subscriptions with a matching event
        
        Args:
            event       name of the event
            pub_data    optional dict of params to be passed to the subscriber
            
        Returns:
            the number of subscriptions that were triggered
        """
        
        #Get all subscriptions with a matching event
        count = 0
        q = db.GqlQuery("SELECT __key__ FROM Subscription WHERE event = :1", event)
        for key in q.run():
            # add a push-queue entry for each notification
            taskqueue.add(url='/pubsub/notify', params={'key':str(key), 'event': event, 'pub_data': json.dumps(pub_data)})
            count = count + 1
        
        #return the number of subscriptions triggered
        return count
    
    @staticmethod    
    def subscribe (event, url, sub_data = None):
        """Subscribe to an event.  
        Args:
            event       name of the event to subscribe to
            url         url to receive a POST when the specified event is published
            sub_data    optional dict of params to be passed to the subscriber.  This can be used to contain 
                        a 'secret' key that will identify the post as coming from this source
        Returns:
            a subscription id
        """
        sub = Subscription(event=event, url=url, data=json.dumps(sub_data))
        return str(sub.put())
        
    @staticmethod    
    def unsubscribe (key):  
        """ Remove an existing subscription. 
        Args:
            key     A subscrption key previously returned by a call to subscribe
        
        Returns: 
            True if the subscription was removed, False if it was not found
        """
        
        sub = Subscription.get(db.Key(encoded=key))
        if sub:
            sub.delete()

        return sub is not None
                
    @staticmethod
    def notify (key, event, pub_data):
        """Send notification to the specified subscription.
        """
        sub = Subscription.get(db.Key(encoded=key))
        if not sub:
            return None
            
        data = {
            'key' : key,
            'event': event,
            'pub_data': pub_data,
            'sub_data': json.loads(sub.data)
        }   

        if sub.url.startswith ('/'):
            #Handle local urls through the task queue
             taskqueue.add(
                url=sub.url, 
                headers = {'Content-Type':'application/json'},
                payload=json.dumps(data))
        else:
            #for external urls use urllib2             
            req = urllib2.Request(sub.url)
            req.add_header('Content-Type', 'application/json')
            response = urllib2.urlopen(req, json.dumps(data))
            
                
#handler for notify - called once for each subscription that is triggered by a published event
class NotifyHandler(webapp2.RequestHandler):
    """Handler for pubsub notifications.  
    This gets called from the taskqueue by tasks added by PubSub.publish()
    """
    
    def post(self): 
        self.response.headers.add_header('Content-Type', 'application/json') 
        r = {'status': 'OK'}
        try:
            PubSub.notify(
                key = self.request.get('key'), 
                event = self.request.get('event'), 
                pub_data = json.loads(self.request.get('pub_data')))
        except Exception, e:
            r['status'] = 'ERR'
            r['message'] = str(e)
        self.response.write(json.dumps( r ))
        
#creates a new task in the task queue
class TaskHandler(webapp2.RequestHandler):
    """This handler acts as a subscribe target and creates a new task in the task queue  
        subdata.channel     specifies the task queue channel
        subdata.taskname    specifies the name to be assigned to the task
            OR
        subdata.pubname     specifies the field name in pub data to use for the task name

    """
    def post(self): 
        self.response.headers.add_header('Content-Type', 'application/json') 
        r = {'status': 'OK'}
        try:
            data = json.loads(self.request.body)
            channel = data['sub_data']['channel']
            name = data['sub_data'].get('taskname')
            if not name:
                name = data['pub_data'].get(data['sub_data'].get('pubname'))
            r['id'] = TaskQueue.add (channel, name, data)
        except Exception, e:
            r['status'] = 'ERR'
            r['message'] = str(e)
        self.response.write(json.dumps( r ))

class TestHandler(webapp2.RequestHandler):
    """This handler expects a json POST, and it returns same json it receives.  Used for testing."""
    def post(self):
        self.response.headers.add_header('Content-Type', self.request.headers['Content-Type']) 
        self.response.write (self.request.body)
    
app = webapp2.WSGIApplication([
    ('/pubsub/notify', NotifyHandler), 
    ('/pubsub/test', TestHandler),
    ('/pubsub/task', TaskHandler)
    ],debug=True)

