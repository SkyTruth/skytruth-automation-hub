from protorpc import messages
from protorpc import message_types
from protorpc import remote

from google.appengine.api import taskqueue
import json
import endpoints
import urllib2
import logging, os
import settings
import inspect 

from endpointshelper import EndpointsHelper
from logger import Logger



package = 'TestAPI'

"""Test API
"""

# Prevent nose from thinking this is a test
__test__ = False

class TestRequest(messages.Message):
    """request message for taskqueue.test"""
    message = messages.StringField(1)

class TestResponse(messages.Message):
    """response message for taskqueue.test"""
    status = messages.StringField(1)
    message = messages.StringField(2)
    info = messages.StringField(3)


    
@endpoints.api(name='test', version='v1.0', 
allowed_client_ids=['314157906781-5k944tnd2e4hvcf0nrc4dl93kgdaqnam.apps.googleusercontent.com'])
class TestApi(remote.Service):
    """Test API
     """
    
    
    @endpoints.method(TestRequest, TestResponse,
                      path='test', http_method='POST',
                      name='test')
    def test(self, request):
        """Test method for debugging conncection and auth issues
        
        This method will return to the caller whatever string is supplied in the 'message' field
        
        The info field in the response contains some debug information
        """
        
        response = TestResponse(message=request.message, status='OK')
        response.info = "USER: %s" % endpoints.get_current_user()                
        try:
            EndpointsHelper.authenticate()
           
            Logger.log (op='test')
        except Exception, err:
            response.status=str(err)
        
        return response
        
                                            