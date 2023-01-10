import sys
import threading
import time
from .logger import log

class Daemon(object):
    running = False

    def __init__(self, func):
        # Connect to the reader
        self.function = func
        log.debug("Initialized daemon")


    def start(self):
        if self.running: return
        log.debug("Starting Thread")
        # Reader Thread
        self.thread = threading.Thread(target=self.function)
        self.thread.setDaemon(True)
        self.running = True;
        self.thread.start()

    def stop(self):
        if not self.running: return
        log.debug("Closing Thread")
        self.running = False
        self.thread.join()

    def isActive(self):
        return self.running
