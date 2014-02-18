import logging, os
import urllib2
import json
import settings


class Logger ():
    """ Wrapper for Loggly API """

    @staticmethod
    def log (**kw):
        """Log arbitrary fields to Loggly
        Args:
            **kw: arguments to be logged
        Returns:
            nothing    
        """

        if settings.DEV_SERVER:
            protocol = 'http'
        else:
            protocol = 'https'
        
        # build loggly url from values in settings.py        
        loggly_url = "%s://logs-01.loggly.com/inputs/%s/tag/%s/" % (protocol, settings.LOGGLY_API_KEY, settings.LOGGLY_APP_NAME)
        
        #TODO: see if we can put app_name in the request header as "Application" instead of in a tag, 
        # then we can use the tag for something else
        
        try:
#            logging.info("SERVER_SOFTWARE: %s" % os.getenv('SERVER_SOFTWARE',''))
            logging.info ("logging to %s" % loggly_url)
            log_data = "PLAINTEXT=" + urllib2.quote(json.dumps(kw))
            response = urllib2.urlopen(loggly_url, log_data) 
            return json.load(response)      
        except Exception, err:
            #write external logging failures to the application log
            logging.error ("Failed to send log entry to Loggly:%s\n%s" % (loggly_url, str(err)))
            
            
            