from protorpc import messages
from protorpc import message_types
from protorpc import remote

import json
import endpoints
import urllib2
import logging, os
import settings

from endpointshelper import EndpointsHelper
from taskqueue import TaskQueue
from logger import Logger

package = 'TaskQueue'

"""TaskQueue API

This API wraps Google App Engine's built in task queue and provides enhanced logging services
"""


class AddTaskRequest(messages.Message):
    """Message to add a task to the task queue
    """
    channel = messages.StringField(1, required=True)
    """Add the task to this channel in the queue.  Use the same channel name to lease the task with taskqueue.lease"""
    
    name = messages.StringField(2, required=True)
    """Name of the task to use for logging purposes"""
    
    content = messages.StringField(3)
    """Can be any string value including json.  This will be returned when the task is leased and can contain additional 
    information needed to complete the task"""

class AddTaskResponse(messages.Message):
    """Response message for taskqueue.add"""
    status = messages.StringField(1, required=True)

class LeaseTaskRequest(messages.Message):
    """Request message for taskqueue.lease"""
    channel = messages.StringField(1, required=True)
    lease_seconds = messages.IntegerField(2)

class LeaseTaskResponse(messages.Message):
    """Response message for taskqueue.lease"""
    status = messages.StringField(1, required=True)
    task_id = messages.StringField(2, required=True)
    task = messages.MessageField(AddTaskRequest,3)
    retry_count = messages.IntegerField(4)

class DeleteTaskRequest(messages.Message):
    """Request message for taskqueue.delete"""
    task_result = messages.StringField(1, required=True)
    lease = messages.MessageField(LeaseTaskResponse,2, required=True)

class DeleteTaskResponse(messages.Message):
    """Response message for taskqueue.delete"""
    status = messages.StringField(1, required=True)

class TestRequest(messages.Message):
    """request message for taskqueue.test"""
    message = messages.StringField(1)

class TestResponse(messages.Message):
    """response message for taskqueue.test"""
    status = messages.StringField(1)
    message = messages.StringField(2)
    info = messages.StringField(3)
    


@endpoints.api(name='taskqueue', version='v1.0', allowed_client_ids=['314157906781-5k944tnd2e4hvcf0nrc4dl93kgdaqnam.apps.googleusercontent.com'])
#@endpoints.api(name='taskqueue', version='v1')
class TaskQueueApi(remote.Service):
    """TaskQueue API
    
    Implements a set of FIFO queues organized into "channels".  Each channel is an independent FIFO queue.  The elements in the queue are "Tasks" which consist of an arbitrary payload that can instruct an external client process what task to perform.
    
    A typical workflow is:
       
    Process A calls taskqueue.add to add tasks to a channel
    Process B calls taskqueue.lease to pull a task from the same channel
    Process B completes the task, whatever that is
    Process B calls tasksqueue.delete to remove the task from the queue
    
    """
    #TODO: Add some usage examples using curl or requests

    
    @endpoints.method(AddTaskRequest, AddTaskResponse,
                      path='add', http_method='POST',
                      name='add')
    def add(self, request):
        """Add a task to the queue
        
        Args:
            request: an AddTaskRequest
        Returns:
            An AddTaskResponse.   status=='OK' on success.  Any other value indicates failure and the task is not added
        """
        response = AddTaskResponse(status = 'OK')
        try:
            EndpointsHelper.authenticate()
            id = TaskQueue.add(request.channel, request.name, request.content)
            #TODO: Maybe we should return the task id?
        except Exception, err:
            response.status=str(err)
        
        return response

    @endpoints.method(LeaseTaskRequest, LeaseTaskResponse,
                      path='lease', http_method='POST',
                      name='lease')
    def lease(self, request):
        """Lease a task in the queue for a specified period of time 
        
        Args: 
            request: a LeaseTaskRequest
            
            
            lease_seconds is the number of seconds to wait for the task to be completed.  If the task is not deleted from the queue
                in that interval, then it will become available again for lease
                
        Returns:
            A LeaseTaskResponse.  status == 'OK' on success.  If there are no tasks available in the requested channel, then 
            status == 'NOT FOUND'.  Any other value for status indicates failure.
            
            the task_id is a unique identifier assigned to the task request when it is added.  It is needed in order to delete the task
                        
            the task attribute in the response is a copy of the AddTaskRequest message that was supplied in the call to taskqueue.add
        """
        response = LeaseTaskResponse(status='NOT FOUND', task_id='')
        try:        
            EndpointsHelper.authenticate()
            task = TaskQueue.lease(request.channel, request.lease_seconds)
            if task:
                response.status='OK'
                response.task = AddTaskRequest(channel=task['channel'], name=task['name'], content=task['content'])
                response.task_id = task['id']
                response.retry_count = task['retry_count']
        except Exception, err:
            response.status=str(err)
        
        return response

    @endpoints.method(DeleteTaskRequest, DeleteTaskResponse,
                      path='delete', http_method='POST',
                      name='delete')
    def delete(self, request):
        """Remove a task from the queue
        
        Args:
            request: A DeleteTaskRequest containing:
                a LeaseTaskRequest that was acquired form a prior call to taskqueue.lease
                a task_result that indicates whether the task was completed successfully 
                
                If the task execution failed and you want it to be re-tried automatically, then do NOT call delete,  
                just come back later after the lease times out and the task will be availble for lease again 
                (unless the retry limit is reached).
            
        Returns:
            A DeleteTaskResponse.  status == 'OK' on success, or 'NOT FOUND' if the task_id does not exist.  Any other value indicates failure.
        """
        response = DeleteTaskResponse(status='NOT FOUND')
        try:        
            EndpointsHelper.authenticate()
            lease = {'id': request.lease.task_id, 'channel': request.lease.task.channel, 'name': request.lease.task.name}
            if TaskQueue.delete (lease, request.task_result):
                response.status='OK'
        except Exception, err:
            response.status=str(err)
        
        return response

    #TODO add method delete_and_add to delete a task and immediately add another task
    
    #TODO add method update_progress that extends the lease duration
 
                                              
app = endpoints.api_server([TaskQueueApi])                                              