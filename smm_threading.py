from pandas import Series, DataFrame
from pandas.io.data import DataReader
from datetime import datetime, date, timedelta
import matplotlib.pyplot as plt
import finsymbols
import threading
import mutex
import Queue
import sys
import download_stock_data


START_DATE = datetime(2000,1,1)
END_DATE = datetime(2013,8,9)


def play_with_data(stock_info_dict):
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
        selected_day = get_friday_before_if_weekend(selected_day)
        try:
            print stock_info_dict[sym].ix[str(selected_day)]
        except KeyError:
            print 'KeyError'

def format_date(date_in_str_form):
    date_split = date_in_str_form.split('/')
    date_formatted = date(int(date_split[2]),int(date_split[1]),int(date_split[0]))
    return date_formatted

def sample_the_data(stock_info_dict):
    while True:
        sym = raw_input("Enter symbol: ")
        if not sym:
            break
        appl_stk = stock_info_dict[sym]
        start_date_formatted = START_DATE
        end_date_formatted = END_DATE
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
        print str(i + 1) + ". " + elem[0] + "-" + '{percent:.1%}'.format(percent=float(elem[1])) 

def get_percent_gain(sym,stk_df, start_day_before):
    try:
        closing_start = stk_df.ix[str(start_day_before)]['Adj Close']
        closing_end = stk_df.ix[str(END_DATE)]['Adj Close']
        return (closing_end - closing_start) / closing_start
    except:
        print "Exception: No information available for " + sym
        return 0

def get_friday_before_if_weekend(date_chosen):
    DAYS_IN_A_WEEK = 7
    FRIDAY_ENUMERATED = 5
    print "The date that you chose is " + str(date_chosen)
    enumerated_day = date_chosen.isoweekday()
    date_to_return = date_chosen
    if enumerated_day > FRIDAY_ENUMERATED:
        print "This day is a weekend date, reporting date the Friday prior"
        dif_to_friday = enumerated_day - FRIDAY_ENUMERATED
        date_to_return -= timedelta(dif_to_friday)
        print "The Friday prior is " + str(date_to_return)
    return date_to_return


sp500_q_lock = threading.Lock()
sp500_q = Queue.Queue()
NUM_SORTING_WORKERS = 5

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

def find_time_stats(stock_info_dict):
    NUM_OF_TOP_ELEMS = 5
    while True:
        time_frame_str = raw_input("Enter time frame (days) before " + str(END_DATE) + ": ")
        if not time_frame_str:
            break
        time_frame_days = int(time_frame_str)
        start_day_before = get_friday_before_if_weekend(END_DATE - timedelta(time_frame_days))
        top_n_stks = []
        smallest_gainer_of_top = 0
        for stk in stock_info_dict:
            ## Thread
            percent_gain = get_percent_gain(stk,stock_info_dict[stk],start_day_before)
            if percent_gain >= smallest_gainer_of_top:
                tuple_to_insert = (stk,percent_gain)
                index_to_insert = find_first_elem_smaller(top_n_stks, tuple_to_insert)
                top_n_stks.insert(index_to_insert,tuple_to_insert)
                top_n_stks = top_n_stks[0:NUM_OF_TOP_ELEMS]
                smallest_gainer_of_top = top_n_stks[len(top_n_stks) - 1][1]
            ## 
        print_stocks_and_gains(top_n_stks)
                
def main():
    stock_info_dict = download_stock_data.download_stock_data()
    find_time_stats(stock_info_dict)
    #sample_the_data(stock_info_dict)
    #play_with_data(stock_info_dict)
    return 0

main()
