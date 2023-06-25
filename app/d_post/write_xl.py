import os
import pandas as pd
from myapp.models import Abonents, Registers2, OrdinaryMails
from gen_shpi import calc_id
import glob
import zipfile
import pdfkit
from django.template.loader import get_template
from weasyprint import HTML, CSS


def zipFiles(files, filename):
    '''pack files to zip'''
    zipObj = zipfile.ZipFile(filename, 'w')
    for n in files:
      zipObj.write(n)
    zipObj.close()


def get_pdf_reg(reg_number):
    '''registry to pdf'''
    Reg = Registers2.objects.filter(id=reg_number)[:1].get()
    abons = Abonents.objects.filter(reg_id=reg_number)
    ord_mails = OrdinaryMails.objects.filter(reg_id=reg_number)
    mails = []  # in case the desired registry is empty
    if abons:
        mails = abons
    if ord_mails:
        mails = ord_mails
    printed = True
    context = {'abons': mails, 'Reg': Reg, 'printed': printed, }
    template = get_template("print_registry.html")
    html = template.render(context)
    filename = 'REG_'+str(Reg.reg_number)+'.pdf'
    options = {'page-size': 'A4',
               'margin-top': '8mm',
               'margin-bottom': '10mm',
               'margin-right': '9mm',
               'margin-left': '9mm',
              }
    pdf = pdfkit.from_string(html, filename, css='print.css', options=options)
    return filename


def write_reg_pdf(numbers, zipfilename):
    '''Group of .pdf registers in zip archive'''
    myfiles = []  # at first, generate .pdf files
    for i in numbers:
        filename = get_pdf_reg(i)
        myfiles.append(filename)  # create list of files
    zipped_file = zipFiles(myfiles, zipfilename)  # pack
    return zipfilename


def generate_xls_file_for_izv_printing(current_registry):  
    '''.xls notices. current_registry = registry id'''
    # add columns names
    mycolumns = ['Codabar', 'ШПИ', '№', 'Адрес', 'Наименование плательщика', '№ документов', 'Дата', 'Инспектор', 'Статус письма']
    df = pd.DataFrame(columns=mycolumns)
    # add content of columns
    rows = []
    if Registers2.objects.get(id=current_registry).notification_id == 'OR':
        ordinary = True
        abons = OrdinaryMails.objects.filter(reg_id=current_registry)
    else:
        ordinary = False
        abons = Abonents.objects.filter(reg_id=current_registry)
    t = 0
    for q in abons:
        t += 1
        if ordinary:
            rows.append(['Codabar', '', t, q.address, q.fio, q.doc_number, '', q.inspector, q.notification_verbose()])
        else:
            rows.append(['Codabar', q.shpi, t, q.address, q.fio, q.doc_number, '', q.inspector, q.notification_verbose()]) 
    for row in rows:
        df.loc[len(df)] = row
    # 'registry printed' flag = True
    rg_in = Registers2.objects.filter(id=current_registry)[:1].get()
    rg = Registers2(id=rg_in.id,
                    reg_number=rg_in.reg_number,
                    reg_date=rg_in.reg_date,
                    reg_real_datetime=rg_in.reg_real_datetime,
                    fns_id=rg_in.fns_id,
                    notification_id=rg_in.notification_id,
                    printed=True)
    rg.save()
    filename = 'REG_'+str(rg_in.reg_number)+'.xlsx'
    df.to_excel(filename, index=False)
    return filename


def write_izv_xls(numbers, zipfilename):
    '''Group .xls files with notices. numbers = registry id'''
    myfiles = []  # list of files
    for i in numbers:
        # create .xls file
        filename = generate_xls_file_for_izv_printing(i)
        myfiles.append(filename)
    zipped_file = zipFiles(myfiles, zipfilename)
    return zipfilename


def create_export_xls(current_registry):
    '''.xls registry'''
    # get a non-recursive list of file paths that matches pattern
    fileList = glob.glob('REGISTRY*.xls', recursive=False)
    for filePath in fileList:
        try:
            os.remove(filePath)
        except OSError:
            print("Error while deleting file")

    # if Registers2.objects.get(id=current_registry).notification_id != 'OR':
    # column's names
    mycolumns = ['Номер заказа', 'ШПИ', 'Масса', 'Стоимость пересылки (с НДС)',
                'Индекс', 'Адрес', 'Телефон', 'ФИО', 'ID_PO']
    df = pd.DataFrame(columns=mycolumns)
    # содержимое
    rows = []
    Reg = Registers2.objects.get(id=current_registry)
    if Registers2.objects.get(id=current_registry).notification_id != 'OR':
        mails = Abonents.objects.filter(reg_id=current_registry)
        for q in mails:
            rows.append(['', q.shpi, '', '', '440008', q.address, '', q.fio, q.abon_id])
    if Registers2.objects.get(id=current_registry).notification_id == 'OR':
        mails = OrdinaryMails.objects.filter(reg_id=current_registry)
        for q in mails:
            rows.append(['', '', '', '', '440008', q.address, '', q.fio, q.abon_id])  
    for row in rows:
        df.loc[len(df)] = row

    filename = 'REGISTRY_'+str(Reg.reg_number)+'.xls'
    df.to_excel(filename, index=False)
    return filename


def delete_tmp_files():
    # get a non-recursive list of file paths that matches pattern
    fileList = glob.glob('REG*.*', recursive=False)
    for filePath in fileList: # iterate over the list of filepaths & remove each file
        try:
            os.remove(filePath)
        except OSError:
            print('Error while deleting file '+filePath)
