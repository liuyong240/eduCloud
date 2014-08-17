import threading, Queue

class run4everThread(threading.Thread):
    def __init__(self, bucket):
        threading.Thread.__init__(self)
        self.bucket = bucket

    def run4ever(self):
        # override this function
        pass

    def run(self):
        try:
            self.run4ever()
        except Exception:
            self.bucket.put(self.__class__.__name__)


