from multiprocessing import  Process,Pipe
class Consumer(Process):
    def __init__(self,pipe):
        Process.__init__(self)
        self.pipe=pipe
    def run(self):
        self.pipe.send('Consumer Words')
        print('Consumer Received',self.pipe.recv())
class product(Process):
    def __init__(self,pipe):
        Process.__init__(self)
        self.pipe=pipe
    def run(self):
        print("Producer Received",self.pipe.recv())
        self.pipe.send("Producer Words")
if __name__=='__main__':
    pipe=Pipe()
    p=product(pipe[0])
    c=Consumer(pipe[1])
    p.daemon=c.daemon=True
    p.start()
    c.start()
    p.join()
    c.join()
    print('End')