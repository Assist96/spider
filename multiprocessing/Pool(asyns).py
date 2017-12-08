from multiprocessing import Pool,Lock
import  time
def function(index):
    print('start process',index)
    time.sleep(3)
    print('end process',index)
if __name__=='__main__':
    pool=Pool(processes=3)
    for i in range(4):
        pool.apply_async(function,(i,))
    print('Started')
    pool.close()
    pool.join()
    print('Subprocess done')