from multiprocessing import Process
import  time
class Myprocess(Process):
    def __init__(self,loop):
        Process.__init__(self)
        self.loop=loop
    def run(self):
        for count in range(self.loop):
            time.sleep(1)
            print('Pid',str(self.pid)," LoopCount:",str(count))
if __name__=='__main__':
    for i in range(2,5):
        p=Myprocess(i)
        p.daemon=True   #daemon 当父进程结束后子进程也会结束。
        p.start()
        p.join()
    print('Main END')