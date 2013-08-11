from pandas import Series, DataFrame
from pandas.io.data import DataReader
from datetime import datetime, date, timedelta
import matplotlib.pyplot as plt
import finsymbols
import threading
import mutex
import Queue
import sys

sp500_q_lock = threading.Lock()
sp500_q = Queue.Queue()
NUM_WORKERS = 16

stock_info_dict_lock = threading.Lock()
stock_info_dict = {}

START_DATE = datetime(2000,1,1)
END_DATE = datetime(2013,8,9)

class DownloadThread(threading.Thread):
    def __init__(self, thread_num):
        super(DownloadThread, self).__init__()
        self.thread_num = thread_num
    def run(self):
        sys.stdout.write('Thread number ' + str(self.thread_num) + ' reporting for duty!\n')
        while True:
            sym = ''
            sp500_q_lock.acquire()
            try:
                sym = sp500_q.get(False)
            except Queue.Empty:
                sp500_q_lock.release()
                sys.stdout.write('Thread number ' + str(self.thread_num) + ' is finished processing.\n')
                return
            sp500_q_lock.release()
            sys.stdout.write('Thread number ' + str(self.thread_num) + ' is downloading ' + sym + '\n')
            curr_df = DataFrame()
            try:
                curr_df = DataReader(sym, "yahoo", START_DATE, END_DATE)
            except IOError:
                sys.stdout.write('Thread number ' + str(self.thread_num) + ' encountered I/O Error while trying to download ' + sym + '\n')
            stock_info_dict_lock.acquire()
            stock_info_dict[sym] = curr_df
            stock_info_dict_lock.release()

def populate_sp500_q():
    sp500 = finsymbols.get_sp500_symbols()
    for co in sp500:
        sp500_q.put(co['symbol'])

def enlist_workers_to_download():
    pool = [DownloadThread(i) for i in range(NUM_WORKERS)]
    for i,thread in enumerate(pool):
        sys.stdout.write('Starting thread number ' + str(i) + '\n')
        thread.start()
    for i,thread in enumerate(pool):
        thread.join()
        sys.stdout.write('Joined thread number ' + str(i) + '\n')

def download_stock_data():
    populate_sp500_q()
    enlist_workers_to_download()
    return stock_info_dict
