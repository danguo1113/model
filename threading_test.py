import threading
import mutex
import Queue
import sys
from pandas import Series, DataFrame
from pandas.io.data import DataReader
from datetime import datetime, date
import matplotlib.pyplot as plt
import finsymbols


stock_q = Queue.Queue()
num_workers = 4

stock_info_dict_lock = threading.Lock()
stock_info_dict = {}

class WorkerThread(threading.Thread):
    def run(self):
        while True:
            try:
                sym = stock_q.get(False)
                sys.stdout.write('Getting info for stock: ' + sym + '\n')
                curr_df = DataReader(sym, "yahoo", datetime(2000,1,1), datetime(2012,1,1))
                stock_info_dict_lock.acquire()
                stock_info_dict[sym] = curr_df
                stock_info_dict_lock.release()
            except Queue.Empty:
                return

def init_q():
    sys.stdout.write('Initializing data\n')
    stock_list = ['AAPL','GOOG','A','BP', 'FB', 'CIS', 'HT', 'XYL','YAHOO']
    for stk in stock_list:
        stock_q.put(stk,True)

def enlist_workers_to_download():
    pool = [WorkerThread() for i in range(num_workers)]
    for thread in pool:
        sys.stdout.write('Starting thread\n')
        thread.start()
    for thread in pool:
        thread.join()
        sys.stdout.write('Joined thread\n')
    
def download_stock_data():
    init_q()
    enlist_workers_to_download()

def play_with_data():
    print stock_info_dict
    while(True):
        sym = raw_input("Enter symbol: ")
        month = raw_input("Enter month: ")
        if not month:
            break
        day = raw_input("Enter day: ")
        if not day:
            break
        year = raw_input("Enter year: ")
        if not year:
            break
        selected_day = date(int(year),int(month),int(day))
        try:
            print stock_info_dict[sym].ix[str(selected_day)]
        except KeyError:
            print 'KeyError'

def main():
    download_stock_data()
    #play_with_data()

main()
