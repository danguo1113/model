from datetime import datetime

from apscheduler.scheduler import Scheduler

sched = Scheduler()
sched.start()

def download_data():
    ## Download


sched.add_interval_job(download_data, hours = 24, start_date = '2013-09-12 01:00')
