#  Сначала обработать исключкния:
#  файл не того расширения
#  формат столбцов не совпадает
#  проверка дат на валидность
#  заполненность столбцов

# from genericpath import exists
import os
# import random
import datetime
import pandas as pd
import numpy as np
# from django.utils import timezone
from myapp.models import Abonents, OrdinaryMails, Status_history, Registers2
from gen_shpi import calc_id
from telegram import send_message



def xls_to_dataframe(path):
  ext = os.path.splitext(path)[1]
  if ext == '.xlsx':
    excel_data_df = pd.read_excel(path, engine='openpyxl').fillna('')  #, sheet_name='Лист1', header=None  , engine='openpyxl'
  if ext == '.xls':
    excel_data_df = pd.read_excel(path).fillna('')
  #print(excel_data_df.columns.ravel())  # заголовок датафрема
  x = np.array([]) #empty array
  cols = len(excel_data_df.columns)
  for h in range (cols):
    x = np.append(x, str(h)) #array of columns names: ['0' '1' '2' '3' '4' '5' '6' '7' ... ]
  df2 = excel_data_df.set_axis(x, axis=1, inplace=False)  #rename columns names to ['0' '1' '2' '3' '4' '5' '6' '7']
  #print(df2.columns.ravel())  # заголовок
  return df2


def read_registry(path, mailtype, registry_date, reg_nbr, fns_id):
    resul = 'err'
    ext = os.path.splitext(path)[1]
    if ext == '.xlsx':
        excel_data_df = pd.read_excel(path, engine='openpyxl').fillna('')
    if ext == '.xls':
        excel_data_df = pd.read_excel(path).fillna('')
    x = np.array([])
    cols = len(excel_data_df.columns)

    for h in range(cols):
        # array of columns names: ['0' '1' '2' '3' '4' '5' '6' '7' ... ]
        x = np.append(x, str(h))
    # rename columns names to ['0' '1' '2' '3' '4' '5' '6' '7']
    df2 = excel_data_df.set_axis(x, axis=1, inplace=False)

    # определяю реальное количество заполненных строк
    real_len = len(df2)
    for i in range(len(df2)):
        if df2['0'].values[i] == '':
            real_len = i
            break
    df3 = df2[:real_len]

    # сначала создаю нов запись в таблицу Registers
    if reg_nbr == 'новый':
        # последний реестр для текущего года:
        if Registers2.objects.filter(reg_date__year=datetime.date.today().year):  # current_year
            last_registry_number = Registers2.objects.filter(reg_date__year=datetime.date.today().year).order_by("-reg_number").first().reg_number
        else:
            last_registry_number = -1
        reg_number = last_registry_number + 1
    else:  # конкретно указанный номер реестра
        reg_number = reg_nbr.split("/")[1]
        # reg_year = reg_nbr.split("/")[0]

    rg = Registers2(reg_number=reg_number,
                    reg_date=registry_date,
                    fns_id=fns_id,
                    notification_id=mailtype)
    rg.save()

    # проверяю наличие столбца ID_PO (26)
    if cols > 25:
        abon_id_exists = True
    else:
        abon_id_exists = False

    if mailtype != "OR":  # заказные
        for i in range(len(df3)):
            shpi = calc_id(1)  # generate shpi
            ID_PO = ''
            if abon_id_exists:  # ID_PO делаю необязательным
                ID_PO = str(df3['26'].values[i])
            ab = Abonents(  shpi=shpi,
                            abon_id=ID_PO,
                            fio=df3['1'].values[i],
                            doc_number=df3['5'].values[i],
                            made_date='',
                            address=df3['0'].values[i],
                            inspector=df3['6'].values[i],
                            telephone='',
                            notification_id=mailtype,
                            record_creation_date=registry_date,
                            fns_id=fns_id,
                            reg_id=Registers2.objects.get(id=rg.id), 
                            )
            ab.save()
            abon_shpi = Abonents.objects.get(shpi=shpi)
            # статус 'в обработке' (0-ой день):
            sh1 = Status_history(shpi = abon_shpi, status_date = pd.to_datetime(registry_date), status_id ='OB')
            sh1.save()
            # статус 'принят в отделении связи' (1-й день (+1 день)):
            sh2 = Status_history(shpi = abon_shpi, status_date = pd.to_datetime(registry_date)+datetime.timedelta(days=1)  , status_id='PR')
            sh2.save()
            # статус 'доставка' (2-й день (+2 дня)):
            sh3 = Status_history(shpi=abon_shpi, status_date=pd.to_datetime(registry_date)+datetime.timedelta(days=2), status_id='DO')
            sh3.save()
            # статус ' хранение' (7-й день (+7 дней)):
            sh4 = Status_history(shpi=abon_shpi, status_date=pd.to_datetime(registry_date)+datetime.timedelta(days=7), status_id='HR')
            sh4.save()
            # статус ' возврат' (30-й день (+30 дней)):
            sh5 = Status_history(shpi=abon_shpi, status_date=pd.to_datetime(registry_date)+datetime.timedelta(days=30), status_id='VZ')
            sh5.save()

    if mailtype == "OR":  # простые
        for i in range(len(df3)):
            ID_PO = ''
            if abon_id_exists:  # ID_PO делаю необязательным
                ID_PO = str(df3['26'].values[i])
            om = OrdinaryMails(abon_id=ID_PO,
                               fio=df3['1'].values[i],
                               doc_number=df3['5'].values[i],
                               made_date='',
                               address=df3['0'].values[i],
                               inspector=df3['6'].values[i],
                               fns_id=fns_id,
                               reg_id=Registers2.objects.get(id=rg.id)
                              )
            om.save()

    # message to telegram
    string = str(rg.fns_id)+' загр реестр №'+str(reg_number)+' на '+str(len(df3))+' отправлений.'
    send_message(string)

    resul = 'ok'
    # delete tmp file:
    if os.path.exists('REGISTRY.xlsx'):
        os.remove('REGISTRY.xlsx')
    if os.path.exists('REGISTRY.xls'):
        os.remove('REGISTRY.xls')
    return [reg_number, real_len, resul]


"""
def read_simpl_registry(path, mailtype, registry_date, reg_nbr, fns_id):
    '''Добавление файлов простых (нерегестрируемых) оправлений'''
    resul = 'err'
    if mailtype != "OR":
        return 'Тип отправления не является простым'
    ext = os.path.splitext(path)[1]
    if ext == '.xlsx':
        excel_data_df = pd.read_excel(path, engine='openpyxl').fillna('')
    if ext == '.xls':
        excel_data_df = pd.read_excel(path).fillna('')
    x = np.array([])
    cols = len(excel_data_df.columns)

    for h in range(cols):
        # x = array of columns names: ['0' '1' '2' '3' '4' '5' '6' '7' ... ]
        x = np.append(x, str(h))
    # rename columns names to ['0' '1' '2' '3' '4' '5' '6' '7']
    df2 = excel_data_df.set_axis(x, axis=1, inplace=False)

    # определяю реальное количество заполненных строк
    real_len = len(df2)
    for i in range(len(df2)):
        if df2['0'].values[i] == '':
            real_len = i
            break
    df3 = df2[:real_len]

    # проверяю поля на заполненность
    for i in range(len(df3)):
        if df3['0'].values[i] == '':
            return [0, real_len, 'не заполнен столбец с порядковым номером в строке ' + str(i+1)]
        if df3['1'].values[i] == '':
            return [0, real_len, 'не заполнен адрес в строке ' + str(i+1)]
        elif df3['2'].values[i] == '':
            return [0, real_len, 'не заполнено наименование плательщика в строке ' + str(i+1)]

    # сначала создаю нов запись в таблицу Registers
    if reg_nbr == 'новый':
        # последний реестр для указанного года:
        if Registers2.objects.filter(reg_date__year=datetime.date.today().year):  # current_year
            last_registry_number = Registers2.objects.filter(reg_date__year=datetime.date.today().year).order_by("-reg_number").first().reg_number
        else:
            last_registry_number = -1
        reg_number = last_registry_number + 1
    else:  # конкретно указанный номер реестра
        reg_number = reg_nbr.split("/")[1]
        # reg_year = reg_nbr.split("/")[0]

    rg = Registers2(reg_number=reg_number,
                    reg_date=registry_date,
                    fns_id=fns_id,
                    notification_id=mailtype)
    rg.save()

    # добавляю список отправлений в таблицу OrdinaryMails
    for i in range(len(df3)):
        om = OrdinaryMails(fio=df3['2'].values[i],
                           doc_number=df3['4'].values[i],
                           made_date=df3['3'].values[i],
                           address=df3['1'].values[i],
                           inspector=df3['5'].values[i],
                           fns_id=fns_id,
                           reg_id=Registers2.objects.get(id=rg.id)
                           )
        om.save()
    # message to telegram
    string = str(rg.fns_id)+' загр простой реестр №'+str(reg_number)+' на '+str(len(df3))+' отправлений.'
    send_message(string)
    resul = 'ok'
    # delete tmp file:
    if os.path.exists('REGISTRY.xlsx'):
        os.remove('REGISTRY.xlsx')
    if os.path.exists('REGISTRY.xls'):
        os.remove('REGISTRY.xls')
    return [reg_number, real_len, resul]
"""


def add_registry_from_izv(path, mailtype, registry_date, fns_id, reg):
    err = 'Записи успешно добавлены'
    #Проверяю, не существует ли уже реестр с таким номером (registers)
    if Registers2.objects.filter(reg_number=reg, reg_date__year=datetime.datetime.now().year).exists():
        err = 'Реестр с таким номером уже существует :('
    else:
        df2 = xls_to_dataframe(path)
        #Проверяю, не заняты ли уже номера ШПИ
        aa = []
        for i in range (len(df2)):
            aa.append(str(df2['1'].values[i]))
        if Abonents.objects.filter(shpi__in=aa).exists():
            err = 'Некоторые идентификаторы уже заняты :('
        else:
            # at first, create a new registry record to Registers table
            rg = Registers2(reg_number = reg, reg_date = registry_date, fns_id = fns_id, notification_id = mailtype) 
            rg.save()
            for i in range (len(df2)):
                # Add records to Abonents table
                ab = Abonents(shpi=df2['1'].values[i],
                          abon_id='',
                          fio=df2['4'].values[i],
                          doc_number=df2['5'].values[i],
                          made_date='',
                          address=df2['3'].values[i],
                          inspector=df2['7'].values[i],
                          telephone='',
                          notification_id=mailtype,
                          fns_id=fns_id,
                          record_creation_date=registry_date,
                          # reg_nmbr=Registers2.objects.get(reg_number=reg,reg_date__year=datetime.datetime.now().year),
                          id=Registers2.objects.get(reg_number=reg,reg_date__year=datetime.datetime.now().year),
                          )
            ab.save()
          
            # Add records to Status_history table 
            # статус 'в обработке' (0-ой день):
            sh1 = Status_history(shpi = ab_shpi, status_date = pd.to_datetime(registry_date), status_id ='OB')      
            if not (Status_history.objects.filter(shpi = ab_shpi, status_date = sh1.status_date, status_id = sh1.status_id).exists()): # if record isn't exist:
                sh1.save()    
            # статус 'принят в отделении связи' (1-й день (+1 день)):
            sh2 = Status_history(shpi = ab_shpi, status_date = pd.to_datetime(registry_date)+datetime.timedelta(days=1)  , status_id='PR')      
            if not (Status_history.objects.filter(shpi = ab_shpi, status_date = sh2.status_date, status_id = sh2.status_id).exists()): # if record isn't exist:
                sh2.save()
            # статус 'доставка' (2-й день (+2 дня)):
            sh3 = Status_history(shpi=ab_shpi, status_date=pd.to_datetime(registry_date)+datetime.timedelta(days=2), status_id='DO')      
            if not (Status_history.objects.filter(shpi = ab_shpi, status_date = sh3.status_date, status_id = sh3.status_id).exists()): # if record isn't exist:
                sh3.save()
            # статус ' хранение' (7-й день (+7 дней)):
            sh4 = Status_history(shpi=ab_shpi, status_date=pd.to_datetime(registry_date)+datetime.timedelta(days=7), status_id='HR')      
            if not (Status_history.objects.filter(shpi = ab_shpi, status_date = sh4.status_date, status_id = sh4.status_id).exists()): # if record isn't exist:
                sh4.save()
            # статус ' возврат' (8-й день (+8 дней)):
            sh5 = Status_history(shpi=ab_shpi, status_date=pd.to_datetime(registry_date)+datetime.timedelta(days=8), status_id='VZ')      
            if not (Status_history.objects.filter(shpi = ab_shpi, status_date = sh5.status_date, status_id = sh5.status_id).exists()): # if record isn't exist:
                sh5.save()

        if os.path.exists(path):  # delete downloaded xlsx file:
            os.remove(path)
        send_message('Восстановлен реестр №'+str(reg)+' на '+str(len(df2))+' отправлений.')
    return [err, ]


def read_scaned_shpi_file(path, registry_status): # путь к файлу, статус отслеживания для отсканированных ШПИ
  ext = os.path.splitext(path)[1]
  if ext == '.xlsx':
    excel_data_df = pd.read_excel(path, engine='openpyxl')  #, sheet_name='Лист1', header=None  , engine='openpyxl'
  if ext == '.xls':
    excel_data_df = pd.read_excel(path)    
  x = np.array([]) #empty array
  for h in range (len(excel_data_df.columns)):
    x = np.append(x, str(h)) #array of columns names: ['0' '1' '2' '3' '4' '5' '6' '7' '8']
  df2 = excel_data_df.set_axis(x, axis=1, inplace=False)  #rename columns names to ['0' '1' '2' '3' '4' '5' '6' '7' '8']
  #добавить информацию об отправлении в базу
  for i in range (len(df2)): 
    # удаляю все предыдущие статусы по данному ШПИ
    abon_shpi = Abonents.objects.get(shpi=df2['0'].values[i])
    Status_history.objects.filter(shpi=abon_shpi).delete()
    # добавляю статус "вручено" VR на сегодня
    sh1 = Status_history(shpi = abon_shpi, status_date = pd.to_datetime('today'), status_id = registry_status)      
    sh1.save()   
  resul = 'ok'
  return resul
