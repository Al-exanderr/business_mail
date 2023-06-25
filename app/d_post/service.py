import os
import io
import datetime
from typing import Counter
from django.utils import timezone
from myapp.models import Abonents, Status_history, Registers2, OrdinaryMails


def clear_database():
    # find and delete shpi in the Status_history table that are not in Abonents table
    Abons = Abonents.objects.all()
    # records that are not in Abonents, but are in Status_history
    extra_records_in_status_hist = Status_history.objects.exclude(shpi__in=Abons)
    print(extra_records_in_status_hist)
    print(extra_records_in_status_hist.count())
    extra_records_in_status_hist.delete()
    # in the Abonents table, find and delete mails that do not belong to any registry
    Regs = Registers2.objects.all()
    extra_records_in_Abonents = Abonents.objects.exclude(reg_number__in=Regs)
    print(extra_records_in_Abonents)
    print(extra_records_in_Abonents.count())
    extra_records_in_Abonents.delete
    pass


def copy_reg_number_to_new_index_field_in_Registers_table():
    Regs = Registers2.objects.all()
    for obj in Regs:
        obj.reg_number_2 = obj.reg_number
        obj.save()
    pass


"""
def copy_Registers2_to_Registers():
    Regs = Registers.objects.all()
    for obj in Regs:
        Regs2 = Registers2(reg_number          = obj.reg_number,
                           reg_date            = obj.reg_date,
                           reg_real_datetime   = obj.reg_real_datetime,
                           fns_id              = obj.fns_id,
                           notification_id     = obj.notification_id,
                           printed             = obj.printed
                           )
        Regs2.save()
    pass """


def copy_Reg_number_of_Registers2_to_id_of_Registers2():
    Regs = Registers2.objects.all()
    for obj in Regs:
        Regs = Registers2(  id=obj.reg_number,
                            reg_number=obj.reg_number,
                            reg_date=obj.reg_date,
                            reg_real_datetime=obj.reg_real_datetime,
                            fns_id=obj.fns_id,
                            notification_id=obj.notification_id,
                            printed=obj.printed
                            )
        Regs.save()
    pass


def copy_records_from_Ordinarymails_to_Abonents():
    Ordinary_mails = OrdinaryMails.objects.all()
    for obj in Ordinary_mails:
        Abons = Abonents(shpi='',
                         abon_id='',
                         fio='',
                         doc_number='',
                         made_date='',
                         address='',
                         telephone='',
                         inspector='',
                         notification_id='OR',
                         record_creation_date=obj.record_creation_date,
                         notification= Registers2.notification
                         )
        Abons.save()
    # pass


def copy_id_records_to_reg_nbr_in_Abonents_table():
    Abons = Abonents.objects.all()
    for obj in Abons:
        Ab = Abonents(shpi=obj.shpi,
                      abon_id=obj.abon_id,
                      fio=obj.fio,
                      doc_number=obj.doc_number,
                      made_date=obj.made_date,
                      address=obj.address,
                      telephone=obj.telephone,
                      inspector=obj.inspector,
                      notification_id=obj.notification_id,
                      record_creation_date=obj.record_creation_date,
                      id=obj.id,
                      reg_nbr=obj.id,
                      fns_id=''
                      )
        Ab.save()
