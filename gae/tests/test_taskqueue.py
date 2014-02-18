
from taskqueue import TaskQueue
import testcasebase 
import time

class TaskQueueTest(testcasebase.AppEngineTestCase):
        
    def testall(self):
        queue = TaskQueue()
        id = queue.add (channel='C', name='N', content=dict(xxx=123))
        self.assertIsNotNone(id)
        lease = queue.lease (channel='C')
        self.assertIsNotNone(lease)
        self.assertEqual(lease['id'], id)
        self.assertEqual(lease['name'], 'N')
        self.assertEqual(lease['channel'], 'C')
        lease = queue.lease (channel='C')
        self.assertIsNone(lease)
        lease = queue.lease (channel='NOT FOUND')
        self.assertIsNone(lease)

        queue.add (channel='C', name='N1', content=dict(xxx=123))
        queue.add (channel='C', name='N2', content=dict(xxx=123))
        lease = queue.lease (channel='C')
        self.assertTrue(queue.delete (lease, 'DONE'))
        self.assertFalse(queue.delete (lease, 'DONE'))
        lease = queue.lease (channel='C')
        self.assertTrue(queue.delete (lease, 'DONE'))
        lease = queue.lease (channel='C')
        self.assertIsNone(lease)

    def testretry(self):
        queue = TaskQueue()
        id = queue.add (channel='RERTY_TEST', name='N', content=dict(xxx=123))
        self.assertIsNotNone(id)
        lease = queue.lease (channel='RERTY_TEST', lease_seconds=1)
        self.assertEqual(id, lease['id'])
        self.assertEqual(lease['retry_count'], 1)
        time.sleep(1)
        lease = queue.lease (channel='RERTY_TEST', lease_seconds=1)
        self.assertEqual(id, lease['id'])
        self.assertEqual(lease['retry_count'], 2)
        time.sleep(1)
        lease = queue.lease (channel='RERTY_TEST', lease_seconds=1)
        self.assertEqual(id, lease['id'])
        self.assertEqual(lease['retry_count'], 3)
        time.sleep(1)
        lease = queue.lease (channel='RERTY_TEST', lease_seconds=1)
        self.assertIsNone(lease)




        
if __name__ == '__main__':
    unittest.main()        