from pandas import Series, DataFrame
from pandas.io.data import DataReader
from datetime import datetime, date
import matplotlib.pyplot as plt
import finsymbols

#def retrieveData(start_date, end_date):
#    stock_lst = ['AAPL']
#    dt = pandas.Panel(dict((stk, pandas.io.data.get_data_yahoo(stk,start_date,end_date)) for stk in stock_lst))
#    return dt

def retrieveData(start_date, end_date):
    sp500 = finsymbols.get_sp500_symbols()
    sym_dict = {}
    for co in sp500:
        try:
            sym = co['symbol']
            print sym
            curr_df = DataReader(sym, "yahoo", datetime(2000,1,1), datetime(2012,1,1)) 
            sym_dict[sym] = curr_df
            print sym_dict
        except IOError:
            print 'I/O Error'
    return sym_dict
        
def playWithData(sym_dict ,start_date, end_date):
    print "Data available after " + start_date + " and on or before " + end_date
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
            print sym_dict[sym].ix[str(selected_day)]
        except KeyError:
            print 'KeyError'

def graphData(dt):
    time_to_adjclose = Series(dt['Adj Close'],dt.index)
    plt.plot(time_to_adjclose)
    plt.show()

def main():
    start_date  ='1/1/2000'
    end_date = '1/1/2012'
    sym_dict = retrieveData(start_date, end_date)
#   playWithData(sym_dict, start_date, end_date)
    #graphData(sym_dict)
    return 0

main()
