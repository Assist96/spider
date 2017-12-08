import multiprocessing
import time
from random import random

from multiprocessing import Queue,Process,Semaphore,Lock

buffer= Queue(10)
empty=Semaphore(2)
full=Semaphore(0)
lock=Lock()
class Consumer(Process):
    def run(self):
        global empty,buffer,full,lock
        while True:
            full.acquire()
            lock.acquire()
            print('Consumer get',buffer.get(False,2))
            time.sleep(1)
            lock.release()
            empty.release()
class Producer(Process):
    def run(self):
        global buffer,full,empty,lock
        while True:
            empty.acquire()
            lock.acquire()
            num=random()
            print('producer put ',num)
            buffer.put(num)
            time.sleep(1)
            lock.release()
            full.release()

if __name__=='__main__':
    p=Producer()
    c=Consumer()
    p.daemon=c.daemon=True
    p.start()
    c.start()
    p.join()
    c.join()
    print('end')

