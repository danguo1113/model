from urllib import urlencode
from urllib2 import urlopen
import urllib2
import csv
import codecs
import pprint
from pandas import DataFrame, Panel
import finsymbols

def get_sp500_str():
    sp500 = finsymbols.get_sp500_symbols()
    sp500_str = ""
    for co in sp500:
        sp500_str += co['symbol']
        sp500_str += " "
    return sp500_str.strip()

def get_data(stks):
    fields = '''Ticker Price PE_Ratio Volume Year_Range Book_Value_per_Share                                                                                                                           
              EBITDA PEG_Ratio'''.split()
    stk_dict = {}
    for i in range(50):
        start = i * 10
        end = i * 10 + 10
        params = urlencode((('s', '+'.join(stks[start: end])), ('f', 'sl1rvwb4j4r5')))
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
            stk_dict[sym] = dict(zip(fields[1:], delimited_row[1:])) 
    stk_df = DataFrame(stk_dict, index=fields[1:])
    return stk_df

def play_with_data(stk_df):
    print "The number of entries is " + str(len(stk_df.columns))
    while True:
        sym = raw_input("Enter symbol: ")
        if not sym:
            return
        pprint.pprint(stk_df[sym])

def main():
    sp500_str = get_sp500_str()
    stk_df = get_data(sp500_str.split())
    play_with_data(stk_df)

main()
