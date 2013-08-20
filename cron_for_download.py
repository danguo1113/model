from datetime import datetime
from apscheduler.scheduler import Scheduler
import time
import logging
import download_stock_data


logging.basicConfig()



def download_data():
    stock_info_dict = download_stock_data.download_stock_data()
    #Should eventually populate a SQL database
    print stock_info_dict


if __name__ == '__main__':
    sched = Scheduler()
    sched.daemonic = False
    sched.start()
    sched.add_interval_job(lambda: download_data(), hours=24)
