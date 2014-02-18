
from google.appengine.api import taskqueue
import json
from logger import Logger
import logging        
    
class TaskQueue ():
    #TODO: Move to settings.py
    RETRY_LIMIT = 3
    
    @staticmethod
    def add(channel, name, content):
        """Add a task to the queue
        
        Args:
            channel     name of the channel that the task will be added to
            name        name of the task - this is only used for logging purposes
            content     a json-serializable object with additional task-specific data.  Can be None
            
        Returns:
            the task id of the newly added task
            
        """
        q = taskqueue.Queue('tasks')
        payload = {'name':name, 'channel': channel, 'content': content}
        task = q.add(taskqueue.Task(payload=json.dumps(payload), tag=channel, method='PULL'))
        Logger.log (op='add', channel=channel, name=name, id=task.name, status='OK')
        return task.name  #Note this is NOT the name that was passed in, this is the auto-assigned id
        
    @staticmethod
    def lease(channel, lease_seconds = 100):
        """Lease a task in the queue for a specified period of time 
        
        Args: 
            channel         name of the channel the task will be leased from.  The next availble task in that 
                            channel will be leased
            lease_seconds   is the number of seconds to wait for the task to be completed.  
                            If the task is not deleted from the queue in that interval, then it will become 
                            available again for lease
                
        Returns:
            a dict with id, name, channel and content

            if no task is availble in the specified channel, returns None
                        
        """
        q = taskqueue.Queue('tasks')

        if not lease_seconds:
            #TODO: Move to settings.py
            lease_seconds = 100
            
        leased_tasks = q.lease_tasks_by_tag (lease_seconds,1, tag=channel)
        retry_count = 0
        if leased_tasks:
            task = json.loads(leased_tasks[0].payload)
            task['id'] = leased_tasks[0].name
            retry_count = leased_tasks[0].retry_count
            task['retry_count'] = retry_count
            if retry_count <= TaskQueue.RETRY_LIMIT:
                Logger.log(op='lease', channel=channel, name=task['name'], id=task['id'], retry_count=retry_count, status='OK')
                return task
            else:
                Logger.log(op='lease', channel=channel, name=task['name'], id=task['id'], retry_count=retry_count, status='RETRY_LIMIT_EXCEEDED')
                TaskQueue.delete(task, 'RETRY_LIMIT_EXCEEDED')
                return None
        else:
            Logger.log(op='lease', channel=channel, status='NOT FOUND')
            return None


    @staticmethod
    def delete(lease, task_result):
        """Remove a task from the queue
        
        Args:
            lease: 
                a lease that was acquired form a prior call to taskqueue.lease
                a task_result that indicates whether the task was completed successfully 
                
                If the task execution failed and you want it to be re-tried automatically, then do NOT call delete,  
                just come back later after the lease times out and the task will be available for lease again 
                (unless the retry limit is reached).
            
        Returns:
            True if the task was deleted, false if the task was not found.
        """

        q = taskqueue.Queue('tasks')
        task=taskqueue.Task(name=lease['id'])
        q.delete_tasks(task)
        if task.was_deleted:
                
            #TODO: It looks like the task that comes back from delete_tasks_by_name() does not include the payload
            #
            # Ideally we could do this:
            #     lease = json.loads(deleted_task[0].payload)
            # but payload always come back as None
            #
            # So the workaround, though clumsy, is to require that the entire lease response to be sent back 
            # with the delete request

                
            Logger.log (op='delete', channel=lease['channel'], name=lease['name'], status='OK', task_result=task_result)
            return True
        else:
            return False

        