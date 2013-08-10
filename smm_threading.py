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
num_workers = 16

stock_info_dict_lock = threading.Lock()
stock_info_dict = {}

start_date  ='1/1/2000'
end_date = '7/4/2013'

class WorkerThread(threading.Thread):
    def __init__(self, thread_num):
        super(WorkerThread, self).__init__()
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
                curr_df = DataReader(sym, "yahoo", format_date(start_date), format_date(end_date))
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
    pool = [WorkerThread(i) for i in range(num_workers)]
    for i,thread in enumerate(pool):
        sys.stdout.write('Starting thread number ' + str(i) + '\n')
        thread.start()
    for i,thread in enumerate(pool):
        thread.join()
        sys.stdout.write('Joined thread number ' + str(i) + '\n')

def download_stock_data():
    populate_sp500_q()
    enlist_workers_to_download()

def play_with_data():
    while(True):
        sym = raw_input("Enter symbol: ")
        if not sym:
            break
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

def format_date(date_in_str_form):
    date_split = date_in_str_form.split('/')
    date_formatted = date(int(date_split[2]),int(date_split[1]),int(date_split[0]))
    return date_formatted

def sample_the_data():
    while True:
        sym = raw_input("Enter symbol: ")
        if not sym:
            break
        appl_stk = stock_info_dict[sym]
        start_date_formatted = format_date(start_date)
        end_date_formatted = format_date(end_date)
        time_difference = end_date_formatted - start_date_formatted
        start_date_formatted += timedelta(1)
        for n in range(int ((end_date_formatted - start_date_formatted).days)):
            curr_date = start_date_formatted + timedelta(n)
            try:
                print stock_info_dict[sym].ix[str(curr_date)]
            except:
                print 'KeyError'

def find_first_elem_smaller(lst,tuple_to_insert):
    if not lst:
        return 0
    for i, elem in enumerate(lst):
        if elem[1] <= tuple_to_insert[1]:
            return i
    return -1

def print_stocks_and_gains(top_n_stks):
    for i, elem in enumerate(top_n_stks):
        print str(i) + ". " + elem[0] + "-" + str(elem[1]) 

def get_percent_gain(stk_df, time_frame):
    end_date_formatted = format_date(end_date) - timedelta(2)
    start_day_before = end_date_formatted - timedelta(time_frame)
    try:
        closing_start = stk_df.ix[str(start_day_before)]['Adj Close']
        closing_end = stk_df.ix[str(end_date_formatted)]['Adj Close']
        return (closing_end - closing_start) / closing_start
    except:
        print "No percent calculated" 
        return 0

def find_time_stats():
    num_of_top_elems = 5
    print "There are " + str(len(stock_info_dict)) + " stocks recorded"
    while True:
        time_frame_str = raw_input("Enter time frame before " + end_date + ": ")
        if not time_frame_str:
            break
        time_frame = int(time_frame_str)
        top_n_stks = []
        smallest_gainer_of_top = 0
        for stk in stock_info_dict:
            print "Procesing stock " + stk
            percent_gain = get_percent_gain(stock_info_dict[stk],time_frame)
            if percent_gain >= smallest_gainer_of_top:
                print stk + " is in the running with a gain of " + str(percent_gain)
                tuple_to_insert = (stk,percent_gain)
                index_to_insert = find_first_elem_smaller(top_n_stks, tuple_to_insert)
                top_n_stks.insert(index_to_insert,tuple_to_insert)
                top_n_stks = top_n_stks[0:5]
                smallest_gainer_of_top = top_n_stks[len(top_n_stks) - 1][1]
        print_stocks_and_gains(top_n_stks)
                
def main():
    download_stock_data()
    find_time_stats()
    #sample_the_data()
    #play_with_data()
    return 0

main()
