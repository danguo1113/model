from datetime import datetime
from apscheduler.scheduler import Scheduler
import time
import logging

logging.basicConfig()

def download_data():
    curr_dir = '/Users/danguo/Desktop/model/'
    file = open(curr_dir + 'output.txt','a')
    file.write("Downloading\n")



if __name__ == '__main__':
    sched = Scheduler()
    sched.daemonic = False
    sched.start()
    sched.add_interval_job(download_data, seconds = 2)
