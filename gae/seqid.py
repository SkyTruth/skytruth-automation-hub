"""
    Generate timestamp-based sequential id values
    @author Paul Woods <paul@skytruth.org>
"""
import time
from datetime import datetime
from google.appengine.ext import db
from google.appengine.api import memcache


class SeqidSeries(db.Model):
    next = db.IntegerProperty(default=0)
    """next seqid value to issue at next db sync"""
    
    interval = db.IntegerProperty(default=1000)
    """interval in milliseconds between db sync points"""
    

def create_seqid():
    """create a seqid using the current system time"""
    return int(time.time() * 1000)


def seqid2str(seqid):
    return datetime.utcfromtimestamp(seqid / 1000.0).strftime('%Y-%m-%d %H:%M:%S.%f')[:23]


class SeqidIssuer(object):
    def __init__(self, series='default'):
        self.series = series
        self.memcache = memcache.Client()
        self.key = "seqid.%s" % series
        self.limit = None

    def issueSeqids(self, n=1):
        """
        Reserve a range of seqids from this series
        Returns a list of integer seqids if successful, otherwise None
        """
        seqids = self._incrementCounter(n)
        if not seqids:
            seqids = self._updateCounter(n)
        if not seqids:
            seqids = self._incrementCounter(n)
        return seqids

    def _incrementCounter(self, n):
        retries = 0
        now = create_seqid()
#        print "_incrementCounter: now=%s" % now
        self.limit = None
        while retries < 3:
            counter = self.memcache.gets(self.key)
            if not counter:
                break
            first, self.limit, interval = counter
            if now - self.limit > interval:
                break

            next = first + n
            if next >= self.limit:
                break
            if self.memcache.cas(self.key, (next, self.limit, interval)):
                return range(first, next)
        return None

    def _updateCounter(self, n):
        def txn(updater, n):
            now = create_seqid()
#            print "_updateCounter: now=%s" % now
            series = SeqidSeries.get_by_key_name(updater.key)
            if series is None:
                #series does not exist, so make a new one
                series = SeqidSeries(key_name=updater.key)
            else:
                if updater.limit and series.next > updater.limit:
                    # someone already updated the db concurrently, so just bail out
                    return None

            # pull out n seqids to return for the current request
            begin = max(now, series.next)
            end = begin + n

            # update series to next block of seqids and store it
            series.next = end + series.interval
            series.put()

            # update memcache
            updater.memcache.set(updater.key, (end, series.next,
                                               series.interval))

            return range(begin, end)

        return db.run_in_transaction(txn, self, n)


class SeqidManager():

    def issueSeqids(self, series='default', qty=1):
        """
        Generate one or more seqids from a seqid series.
        Use qty to specify how many you want.
        seqids are guaranteed to be unique within a series
        and to always increase in value.
        They may have gaps in the sequence.
        Seqids are retured in a string formatted as a
        timestamp with milliseconds.  e.g. 2012-04-18 01:02:03.456
        This function returns a list of strings sorted in ascending order
        
        The timestamp will always be within a minute or so of the current system time
        
        Note that when running in GAE, system times on different server instances may not be perfectly synchronized, 
        so the time base for generate seqids may jump forward from one call to the next.
        
        """
        issuer = SeqidIssuer(series)
        seqids = issuer.issueSeqids(qty)
        if seqids:
            return [seqid2str(s) for s in seqids]
        else:
            return None
            
            
       
        