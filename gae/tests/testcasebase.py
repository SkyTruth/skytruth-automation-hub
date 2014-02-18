import unittest2
from google.appengine.api import memcache
from google.appengine.ext import db
from google.appengine.ext import testbed
from google.appengine.api import taskqueue
import webtest
import base64
import json
import os

class AppEngineTestCase(unittest2.TestCase):

    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_all_stubs()
        
        self.taskqueue_stub = self.testbed.get_stub(testbed.TASKQUEUE_SERVICE_NAME)
        # need this kludge to tell the stup where to find queue.yaml
        self.taskqueue_stub._root_path = os.path.dirname(os.path.dirname( __file__ ))
        
        # For convenience, the subclass can implement 'set_up' rather than overriding setUp()
        # and calling this base method.
        if hasattr(self, 'set_up'):
            self.set_up()
        
    def tearDown(self):
        if hasattr(self, 'tear_down'):
            self.tear_down()
            
        self.testbed.deactivate()         

    def executeTask (self, queue='default'):
        """Execute the first task in the task queue
        NB: this assumes that the task is an url and the method is POST.   
        This will not work for GET or for deferred function calls that also use the task queue
        """
        tasks = self.taskqueue_stub.GetTasks(queue)
        if tasks:
            task = tasks[0]
            self.taskqueue_stub.DeleteTask (queue, task['name'])
            params = base64.b64decode(task["body"])
            if dict(task['headers']).get('Content-Type') == 'application/json':
                return self.testapp.post_json(task["url"], json.loads(params))
            else:
                return self.testapp.post(task["url"], params)

