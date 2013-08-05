from urllib import urlencode
from urllib2 import urlopen
import urllib2
import csv
import codecs
import pprint
from pandas import DataFrame, Panel
import finsymbols
import threading
import mutex
import Queue
import sys

sp500_divided_q = Queue.Queue()
num_workers = 16

stock_info_dict_lock = threading.Lock()
stock_info_dict = {}

stock_info_df = DataFrame()

fields = '''Ticker Price PE_Ratio Volume Year_Range Book_Value_per_Share EBITDA PEG_Ratio'''.split()

class WorkerThread(threading.Thread):
    def run(self):
        while True:
            try:
                stk_group = sp500_divided_q.get(False)
                sys.stdout.write('Downloading the group: ' +  str(stk_group) + '\n')
            except Queue.Empty:
                sys.stdout.write('Finished processing.\n')
                return
            try:
                params = urlencode((('s', '+'.join(stk_group)), ('f', 'sl1rvwb4j4r5')))
                url = 'http://finance.yahoo.com/d/quotes.csv'
                url = '?'.join((url, params))
                response = urlopen(url)
                response_str = response.read()
                for row in response_str.strip().split('\n'):
                    delimited_row = row.strip('\r').split(',')
                    delimited_row = delimited_row
                    sym = delimited_row[0][1:-1]
                    print "Processing statistics about stock: " + sym
                    delimited_row[4] = delimited_row[4][1:-1]
                    stock_info_dict_lock.acquire()
                    stock_info_dict[sym] = dict(zip(fields[1:], delimited_row[1:]))
                    stock_info_dict_lock.release()
            except IOError:
                sys.stdout.write('I/O Error\n')

def get_sp500_str():
    sp500 = finsymbols.get_sp500_symbols()
    sp500_str = ""
    for co in sp500:
        sp500_str += co['symbol']
        sp500_str += " "
    return sp500_str.strip()

def populate_sp500_q():
    sp500_str = get_sp500_str()
    sp500_delimited = sp500_str.split()
    for i in range(50):
        start = i * 10
        end = i * 10 + 10
        small_lst = sp500_delimited[start:end]
        sp500_divided_q.put(small_lst)

def enlist_workers_to_download():
    pool = [WorkerThread() for i in range(num_workers)]
    for thread in pool:
        sys.stdout.write('Starting thread\n')
        thread.start()
    for thread in pool:
        thread.join()
        sys.stdout.write('Joined thread\n')

def format_data():
    global stock_info_df
    print len(stock_info_dict)
    stock_info_df = DataFrame(stock_info_dict, index=fields[1:])

def play_with_data():
    print "The number of entries is " + str(len(stock_info_df.columns))
    while True:
        sym = raw_input("Enter symbol: ")
        if not sym:
            return
        pprint.pprint(stock_info_df[sym])

def main():
    populate_sp500_q()
    enlist_workers_to_download()
    format_data()
    play_with_data()

main()
