from datetime import datetime
import json
import string

import webapp2
from google.appengine.ext import db
from google.appengine.api import memcache
from google.appengine.api import search 

from seqid import SeqidIssuer, seqid2str
from pubsub import PubSub





class GeoFeed ():
                    
    @staticmethod
    def publish (**kw):
        issuer = SeqidIssuer(series=kw['topic'])
        seqid = issuer.issueSeqids()[0]
        doc = search.Document(
            doc_id = kw['key'],
            fields=[
                search.AtomField(name='topic', value=kw['topic']),
                search.AtomField(name='key', value=kw['key']),
                search.GeoField(name='location', 
                    value=search.GeoPoint(kw.get('latitude',0), kw.get('longitude',0))),
                search.AtomField(name='published', value=seqid2str(seqid)),
                search.AtomField(name='url', value=kw.get('url', '')),
                search.TextField(name='content', value=kw.get('content', ''))
                ],
                rank = seqid /1000  # rank is int32, so convert seqid from milliseconds to seconds
                )
        index_name = GeoFeed._indexname(kw['topic'])
        index = search.Index(name=index_name)
        id = index.put(doc)[0].id
        PubSub.publish(event=index_name, pub_data={'key':kw['key']})
        return id
                
    @staticmethod
    def list (topic):
        index = search.Index(name=GeoFeed._indexname(topic))
        query_string = 'topic:%s' % topic
        results = index.search(
            search.Query(query_string=query_string,
              options=search.QueryOptions(limit=200)) )   
        for result in results:
            yield GeoFeed._doc2dict (result)

    @staticmethod
    def get (topic, key):
        index = search.Index(name=GeoFeed._indexname(topic))
        return GeoFeed._doc2dict(index.get(key))

    @staticmethod
    def _indexname(topic):
        return "GeoFeed.%s" % (topic)

    @staticmethod
    def _doc2dict (doc):
        if not doc: 
            return None
        result = {f.name:f.value for f in doc.fields}
        # unpack location field
        location = result.get('location')
        if location:
            del result['location']
            result['latitude'] = location.latitude
            result['longitude'] = location.longitude
        return result
        
class ListHandler(webapp2.RequestHandler):
    """This handler expects a json POST, and it returns same json it receives.  Used for testing."""
    def get(self, topic):
        format = self.request.get('format','json')  
        t = self.template.get(format)
        if not t:
            t = self.template.get('json')
            
        self.response.headers['Content-Type'] = t['content-type']
        
        self.response.write(t['header'])
        first = True
        for item in GeoFeed.list(topic):
            if not first:
                self.response.write(t['separator'])
            else:
                first = False

            self.response.write(t['item'].safe_substitute(item))
        self.response.write(t['footer'])

    def __init__(self, request, response):
        # Set self.request, self.response and self.app.
        self.initialize(request, response)       
         
        self.template = {'json': {}}        
        self.template['json']['content-type'] = 'application/json'
        self.template['json']['header'] = '['
        self.template['json']['footer'] = ']'
        self.template['json']['item'] = string.Template("""
            { "topic": "$topic",
              "key": "$key"
            }""")  
        self.template['json']['separator'] = r','
    
class GetHandler(webapp2.RequestHandler):
    """This handler expects a json POST, and it returns same json it receives.  Used for testing."""
    def get(self, topic, key):
        self.response.headers.add_header('Content-Type', 'application/json') 
        r = {'status': 'OK'}
        try:
            item = GeoFeed.get(topic, key)
            if not item:
                r['status'] = 'NOT FOUND'
            r['item'] = item
        except Exception, e:
            r['status'] = 'ERR'
            r['message'] = str(e)
        self.response.write(json.dumps( r ))

        
# Url structure
#
# Get a list of feed items, most recent first, geojson 
#   /geofeed/<topic>    
# Optional format (rss, json, kml, etc)     
#   /geofeed/<topic>?f=<format> 
# Get a single feed item - json  
#   /geofeed/<topic>/<key>
#    

app = webapp2.WSGIApplication([
    webapp2.Route('/geofeed/<topic><:/?>', handler=ListHandler, name='list'), 
    webapp2.Route('/geofeed/<topic>/<key>', handler=GetHandler, name='get'), 
    ],debug=True)



