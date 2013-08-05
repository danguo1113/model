from pandas import Series, DataFrame
from pandas.io.data import DataReader
from datetime import datetime, date
import matplotlib.pyplot as plt
import finsymbols
import threading
import mutex
import Queue
import sys

sp500_q = Queue.Queue()
num_workers = 16

stock_info_dict_lock = threading.Lock()
stock_info_dict = {}

class WorkerThread(threading.Thread):
    def run(self):
        while True:
            try:
                sym = sp500_q.get(False)
                sys.stdout.write('Downloading ' + sym + '\n')
            except Queue.Empty:
                sys.stdout.write('Finished processing. GB\n')
                return
            try:
                curr_df = DataReader(sym, "yahoo", datetime(2000,1,1), datetime(2012,1,1))
                stock_info_dict_lock.acquire()
                stock_info_dict[sym] = curr_df
                stock_info_dict_lock.release()
            except IOError:
                sys.stdout.write('I/O Error\n')
                

def populate_sp500_q():
    sp500 = finsymbols.get_sp500_symbols()
    for co in sp500:
        sp500_q.put(co['symbol'])

def enlist_workers_to_download():
    pool = [WorkerThread() for i in range(num_workers)]
    for thread in pool:
        sys.stdout.write('Starting thread\n')
        thread.start()
    for thread in pool:
        thread.join()
        sys.stdout.write('Joined thread\n')

def download_stock_data():
    populate_sp500_q()
    enlist_workers_to_download()

def play_with_data():
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
    start_date  ='1/1/2000'
    end_date = '1/1/2012'
    download_stock_data()
    play_with_data()
    return 0

main()
