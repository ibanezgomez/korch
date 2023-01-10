from datetime import datetime, timedelta
import time
import threading
from .logger import log
from .daemon import Daemon

# Some utility classes / functions first
class AllMatch(set):
    """Universal set - match everything"""
    def __contains__(self, item): return True

allMatch = AllMatch()

def conv_to_set(obj):  # Allow single integer to be provided
    if isinstance(obj, (int,int)):
        return set([obj])  # Single item
    if not isinstance(obj, set):
        obj = set(obj)
    return obj

# The actual Job class
class Job(object):
    mins   = conv_to_set(allMatch)
    hours  = conv_to_set(allMatch)
    days   = conv_to_set(allMatch)
    months = conv_to_set(allMatch)
    dow    = conv_to_set(allMatch)
    timestamp = 0
    
    action = None
    args   = ()
    kwargs = {}
    
    # kwargs: min, hour, day, month, dow, timestamp
    def __init__(self, action, args=(), kwargs={}, min=allMatch, hour=allMatch, 
                       day=allMatch, month=allMatch, dow=allMatch, timestamp=0):

        self.mins   = conv_to_set(min)
        self.hours  = conv_to_set(hour)
        self.days   = conv_to_set(day)
        self.months = conv_to_set(month)
        self.dow    = conv_to_set(dow)
        self.action    = action
        self.args      = args
        self.kwargs    = kwargs
        self.timestamp = int(timestamp)
        

    def check(self, t):
        """Return True if this job should trigger at the specified datetime"""
        return (((t.minute     in self.mins) and
                 (t.hour       in self.hours) and
                 (t.day        in self.days) and
                 (t.month      in self.months) and
                 (t.weekday()  in self.dow) and
                 (self.timestamp <= 0 )) or 
                 (self.timestamp >  0 and 
                  self.timestamp <= int(t.strftime('%s')) and
                  self.timestamp >  int(t.strftime('%s')) - 60))

    def run(self):
        # ToDo: If process is long timed, scheduler will be stuck, use subprocess
        self.action(*self.args, **self.kwargs)
    
            
            
# The scheduler itself
class Scheduler(Daemon):
    jobs = {}
        
    def __init__(self):
        log.debug("Initializing Scheduler")
        super().__init__(self.run)
        
    def addJob(self, id, job):
        log.info("Adding Job \""+id+"\"")
        self.jobs[id] = job
        
    def deleteJob(self, id):
        log.info("Deleting Job \""+id+"\"")
        if id in self.jobs:
            del self.jobs[id]
                
    def getJobs(self):
        return self.jobs
                
    def getJob(self,id):
        if id in self.jobs:
            return self.jobs[id]
        else:
            return None
        
    def isJob(self,id):
        return True if id in self.jobs else False

    def run(self):
        while self.running:
            todel = []
            for id in self.jobs:
                if self.jobs[id].check(datetime.now()):
                    log.info("Executing job \""+id+"\"")
                    try: threading.Thread(target=self.jobs[id].run).start()
                    except: log.error("Thread %s Error" % id, exc_info=True)
                    if self.jobs[id].timestamp > 0: todel.append(id)
            
            for i in todel: self.deleteJob(i)      
            time.sleep(60)
            
