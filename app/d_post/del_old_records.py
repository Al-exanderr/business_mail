
from myapp.models import Status_history, Abonents
import os
import datetime
import pandas as pd
import numpy as np
from django.utils import timezone


def del_old_shpi():  # later than 2 mounths
    target_date1 = pd.to_datetime('today')-datetime.timedelta(days=62)   # 62
    Abonents.objects.filter(record_creation_date__lt=target_date1).delete()

    target_date2 = pd.to_datetime('today')-datetime.timedelta(days=730)   # 365 x 2
    Status_history.objects.filter(status_date__lt=target_date2).delete()
