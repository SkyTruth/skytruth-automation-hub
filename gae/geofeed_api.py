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

from seqid import SeqidIssuer, seqid2str
from endpointshelper import EndpointsHelper
from logger import Logger
from geofeed import GeoFeed


package = 'GeoFeedAPI'

"""GeoFeed API
"""

class SeqidResponse(messages.Message):
    """Response message for geofeed.seqid method"""
    status = messages.StringField(1)
    series = messages.StringField(2)
    seqid_datetime = messages.StringField(3)
    seqid_int = messages.IntegerField(4)

class TestRequest(messages.Message):
    """request message for taskqueue.test"""
    message = messages.StringField(1)

class TestResponse(messages.Message):
    """response message for taskqueue.test"""
    status = messages.StringField(1)
    message = messages.StringField(2)
    info = messages.StringField(3)

class FeedItem(messages.Message):
    topic = messages.StringField(1, required=True)
    key = messages.StringField(2, required=True)
    url = messages.StringField(3)
    latitude = messages.FloatField(4)
    longitude = messages.FloatField(5)
    content = messages.StringField(6)
    published = messages.StringField(7)
    
class PublishResponse(messages.Message):
    """response message for geofeed.publish"""
    status = messages.StringField(1)

class ListRequest(messages.Message):
    """message for retrieving a list of feed items"""
    topic = messages.StringField(1, required=True)

class ListResponse(messages.Message):
    """response message for geofeed.list"""
    status = messages.StringField(1)
    items = messages.MessageField(FeedItem, 2, repeated=True)

class GetRequest(messages.Message):
    """message for retrieving a single feed items"""
    topic = messages.StringField(1, required=True)
    key = messages.StringField(2, required=True)

class GetResponse(messages.Message):
    """response message for geofeed.get"""
    status = messages.StringField(1)
    item = messages.MessageField(FeedItem, 2)
    
@endpoints.api(name='geofeed', version='v1.0', allowed_client_ids=['314157906781-5k944tnd2e4hvcf0nrc4dl93kgdaqnam.apps.googleusercontent.com'])
#@hub_api.api_class(resource_name='geofeed')
class GeoFeedApi(remote.Service):
    """GeoFeed API
     """

    SEQUENCE_RESOURCE = endpoints.ResourceContainer(
            message_types.VoidMessage,
            series=messages.StringField(1))
                
    @endpoints.method(SEQUENCE_RESOURCE, SeqidResponse,
                      path='seqid/{series}', http_method='GET',
                      name='seqid')
    def seqid(self, request):
        """Get a new seqid from the specified series
         """
        response = SeqidResponse(status='OK')
        try:
            EndpointsHelper.authenticate()
            issuer = SeqidIssuer(series=request.series)
            seqid = issuer.issueSeqids()[0]

            response.series = issuer.series
            response.seqid_int = seqid             
            response.seqid_datetime = seqid2str (seqid)
            
        except Exception, err:
            response.status=str(err)

        return response

    @endpoints.method(FeedItem, PublishResponse,
                      path='publish', http_method='POST',
                      name='publish')
    def publish(self, request):
        """Publish a new item to a feed.
         """
        response = PublishResponse(status='OK')
        try:
            EndpointsHelper.authenticate()
            GeoFeed.publish(**EndpointsHelper.message2dict(request))
        except Exception, err:
            response.status=str(err)

        return response
            
    @endpoints.method(ListRequest, ListResponse,
                      path='list', http_method='POST',
                      name='list')
    def list(self, request):
        """Retrieve a list of recent items in a feed
        """
        response = ListResponse(status='OK')
        try:
            EndpointsHelper.authenticate()
            response.items = [FeedItem(**item) for item in GeoFeed.list(topic=request.topic)]
        except Exception, err:
            response.status=str(err)

        return response

    @endpoints.method(GetRequest, GetResponse,
                      path='get', http_method='POST',
                      name='get')
    def get(self, request):
        """Retrieve a specified feed item
        """
        response = GetResponse(status='OK')
        try:
            EndpointsHelper.authenticate()
            item = GeoFeed.get(request.topic, request.key)
            if item:
                response.item = FeedItem(**item)
            else:
                response.status='NOT FOUND'
        except Exception, err:
            response.status=str(err)

        return response


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
        
#app = endpoints.api_server([hub_api])                                              
#app = endpoints.api_server([GeoFeedApi])                                              