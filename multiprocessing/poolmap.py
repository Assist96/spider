from multiprocessing import Pool
import requests
from requests.exceptions import ConnectionError
def scrape(url):
    try:
        print(requests.get(url))
    except ConnectionError:
        print("Error occured",url)
    finally:
        print("URL:",url,"Scraped")
if __name__=='__main__':
    pool=Pool()
    urls=[
        'https://www.baidu.com',
        'http://www.meituan.com',
        'http://www.google.com',
        'http://www.meizitu.com'

    ]
    pool.map(scrape,urls)