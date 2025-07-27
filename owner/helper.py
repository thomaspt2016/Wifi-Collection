from datetime import datetime, date
from dateutil.relativedelta import relativedelta

def get_next_month_25th():
    today = date.today()
    
    # Use relativedelta to easily add one month
    next_month = today + relativedelta(months=1)
    
    # Set the day to the 25th
    next_month_25th = next_month.replace(day=25)
    
    return next_month_25th
