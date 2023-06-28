#  Формат ШПИ
#  ХХХХХХ........  случайное число
#  ......ХХ......  номер месяца с 1 января 2020
#  ........ХХ....  сегодняшнее число
#  ..........Х...  идентификатор налоговой
#  ...........Х..  идентификатор с уведомлением или без
#  ............Х.  зарезервированный символ = 0
#  .............Х  СRС


from myapp.models import CustomUser, Abonents
from django.utils import timezone
import os
import random
import datetime
import pandas as pd
import numpy as np


fns = CustomUser.objects.filter(username='admin')[:1]


def MONTH():
    M = (pd.to_datetime('today').to_period('M') - pd.to_datetime('2000-01-01').to_period('M')).n 
    if M>99:
        M = M-100
        if M>99:
            M = M-100
    return M


def CRC(num: str) -> int:
    weights_even = [0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0]
    weights_odd  = [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1]
    sum_even = 0
    sum_odd = 0
    for i in range(len(num)):
        sum_even += weights_even[i] * int(num[i])
        sum_odd  += weights_odd[i] * int(num[i])
    sum = sum_even + sum_odd*3
    sum = 10 - (sum % 10)
    if sum == 10:
        sum = 0
    return sum


def calc_id(ZAKAZNOYE):
    finished = False
    n = 0
    while not finished:

        # RND = random.randrange(100000, 999999, 1)
        RND = 44000
        # if kol_generated.count() > 700:
        # RND = 440011
        last_index_digit = random.randrange(0, 9, 1)

        DAY = str(pd.to_datetime('today').day)
        if len(DAY) == 1:
            DAY = '0'+DAY

        N_ID      = random.randrange(0, 9, 1)
        ZAKAZNOYE = random.randrange(0, 9, 1)
        RESERVED  = random.randrange(0, 9, 1)
        #         6            2           2           1             1                1
        SHPI = str(RND) + str(last_index_digit) + str(MONTH()) + str(DAY) + str(N_ID) + str(ZAKAZNOYE) + str(RESERVED)
        #                    1
        SHPI = SHPI + str(CRC(SHPI))

        # SHPI is exists?
        if not (Abonents.objects.filter(shpi=SHPI).exists()):
            SHPI_final = SHPI
            finished = True
    return SHPI_final
