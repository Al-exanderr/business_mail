from django.utils import timezone
from django.shortcuts import render, redirect
from .models import Abonents, Status_history, Registers2, OrdinaryMails
from .forms import (Request_Track_Form, Login_Form,
                    UploadRegistryForm, UploadRegistryFormAdmin,
                    UploadScanForm, ViewRegistersForm,
                    StatisticsForm)
import os
from django.contrib.auth import authenticate, login, logout
from django.conf import settings
from django.views.decorators.csrf import csrf_protect
from read_xl import (read_registry,
                     read_scaned_shpi_file, add_registry_from_izv)
from write_xl import (generate_xls_file_for_izv_printing,
                      create_export_xls,
                      delete_tmp_files, write_reg_pdf, write_izv_xls,
                      get_pdf_reg)
from external_funcs import getTupleOfMissingRegistries
from datetime import datetime
from weasyprint import HTML  # CSS
from django.template.loader import get_template
from django.template.loader import render_to_string
import tempfile
from django.http import FileResponse
from django.http import HttpResponse  # HttpRequest
from django.http.request import QueryDict
from django.utils.dateparse import parse_date
import pdfkit
from telegram import send_message, send_db_to_telegram
import redis
from shutil import copy
from django.core.paginator import Paginator
from django.views import View
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from other_func import get_client_ip, handle_uploaded_file
from django.utils.decorators import method_decorator
from django import forms
import json
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import AbonentsSerializer

r = redis.StrictRedis(host=settings.REDIS_HOST,
                      port=settings.REDIS_PORT,
                      db=settings.REDIS_DB,
                      decode_responses=True)


def index(request):
    if request.user.is_authenticated:
        return render(request, 'index.html')
    else:
        return redirect('/myapp/login/')


class Login(View):
    def post(self, request):
        form = Login_Form(request.POST)
        if form.is_valid():
            username = form.cleaned_data['user']
            password = form.cleaned_data['passwd']
            send_message('Попытка залогиниться: '+username+' IP: '+get_client_ip(request))
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)   # привязать к сессии авторизованного пользователя               
                    return redirect('/myapp/') # Redirect to a success page.
                else:
                    return HttpResponse( 'Disabled account!' ) # Return a 'disabled account' error message
            else:
                return HttpResponse( '<p>Неправильный логин или пароль.</p>  <a href="/myapp/login/">Назад</a>' )

    def get(self, request):
        form = Login_Form()
        return render(request, 'login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('/myapp/login/')


# add registry file
@method_decorator(csrf_protect, name='dispatch')
class AddRegistry(LoginRequiredMixin, View):
    def post(self, request):
        if request.user.username == 'admin':
            form = UploadRegistryFormAdmin(request.POST, request.FILES)
        else:
            form = UploadRegistryForm(request.POST, request.FILES)

        if form.is_valid():
            reg_nbr = 'новый'  # default value
            mailtype = form.cleaned_data['choise_field']
            reg_date = timezone.now()
            fns_id = request.user.fns_id
            if request.user.username == 'admin':
                reg_date = datetime.strptime(request.POST['reg_date'], '%Y-%m-%d')
                reg_nbr = form.cleaned_data['choise_registry']  # number of reg or 'новый'
                fns_id = form.cleaned_data['choise_ifns']
            ext = os.path.splitext(str(request.FILES['file']))[1]  # file extansion
            if ext == '.xlsx':
                fn = 'REGISTRY.xlsx'
            if ext == '.xls':
                fn = 'REGISTRY.xls'
            handle_uploaded_file(request.FILES['file'], fn)
            cur_reg = read_registry(fn, mailtype, reg_date, reg_nbr, fns_id)
            return HttpResponse('<p>'+'Реестр №'+str(cur_reg[0])+' на '+str(cur_reg[1])+' абонентов загружен.'+'</p><a href="/myapp/add_registry/">Назад </a><a href="/myapp/view_registers/">Просмотр реестров </a><a href="/myapp/">Главная</a>')
        else:
            return HttpResponse('<p>'+'Что-то пошло не так... '+'</p><a href="/myapp/print_notices/">Назад  </a><a href="/myapp/">Главная</a>')

    def get(self, request):
        if request.user.username == 'admin':
            form = UploadRegistryFormAdmin()
            form.fields['choise_registry'].widget = forms.Select(
                                        choices=getTupleOfMissingRegistries())
        else:
            form = UploadRegistryForm()
        return render(request, 'upload_registry.html', {'form': form})


# add izv file xlsx
@method_decorator(csrf_protect, name='dispatch')
class AddNoticesXLSX(LoginRequiredMixin, View):
    def post(self, request):
        form = UploadRegistryFormAdmin(request.POST, request.FILES)
        if form.is_valid():
            mailtype = form.cleaned_data['choise_field']
            reg_date = timezone.now()
            fns_id = request.user.fns_id
            reg_date = request.POST['reg_date']
            fns_id = form.cleaned_data['choise_ifns']
            reg = form.cleaned_data['choise_registry']
            ext = os.path.splitext(str(request.FILES['file']))[1]  # file entension
            fn = 'registry_from_izv.xlsx'
            handle_uploaded_file(request.FILES['file'],fn)
            # add data from file to database:
            cur_reg = add_registry_from_izv(fn, mailtype, reg_date, fns_id, reg)
            return HttpResponse('<p>'+str(cur_reg[0])+'</p><a href="/myapp/add_registry/">Назад </a><a href="/myapp/view_registers/">Просмотр реестров </a><a href="/myapp/">Главная</a>')
        else:
            return HttpResponse('<p>'+'Что-то пошло не так... '+'</p><a href="/myapp/print_notices/">Назад  </a><a href="/myapp/">Главная</a>')

    def get(self, request):
        form = UploadRegistryFormAdmin()
        t = getTupleOfMissingRegistries()
        form.fields['choise_registry']= forms.CharField(required=False, widget=forms.Select(choices=t), label='Номер реестра:')
        return render(request, 'upload_registry.html', {'form': form,})


# add scaned SHPI file
@method_decorator(csrf_protect, name='dispatch')
class AddScanShpi(LoginRequiredMixin, View):
    resul = 'Операция не выполнена.'

    def post(self, request):
        form = UploadScanForm(request.POST, request.FILES)
        if form.is_valid():
            # status of scanned SHPI's, 'ВРУЧЕНО' by default
            registry_status = form.cleaned_data['ch_field']
            ext = os.path.splitext(str(request.FILES['file']))[1]
            if ext == '.xlsx':
                fn = 'REGISTRY.xlsx'
            if ext == '.xls':
                fn = 'REGISTRY.xls'
            handle_uploaded_file(request.FILES['file'], fn)
            resul = read_scaned_shpi_file(fn, registry_status)
            return HttpResponse('<p>'+resul+'</p><a href="/myapp/add_scan_shpi/">Назад  </a><a href="/myapp/">Главная</a>')

    def get(self, request):
        form = UploadScanForm()
        return render(request, 'upload_scan.html', {'form': form})


class TrackSHPI(LoginRequiredMixin, View):
    def post(self, request):
        form = Request_Track_Form(request.POST)
        if form.is_valid():
            current_shpi = form.cleaned_data['shpi']
            return redirect('/myapp/track_shpi/'+str(current_shpi)+'/')

    def get(self, request):
        form = Request_Track_Form()
        return render(request, 'track.html', {'form': form})


@login_required()
def track_detail_shpi(request, shpi):
    abonen = list(Abonents.objects.filter(shpi=shpi)[:1])
    if not abonen:
        return HttpResponse('<p>Указанный идентификатор не существует.</p> <a href="/myapp/track_shpi/">Назад</a>')
    else:
        # tracking no longer than 7 months
        before = timezone.now() - timezone.timedelta(days=210)
        if request.user.username == 'admin':
            before = datetime(2021, 1, 1)  # unlim for admin)
        info = Status_history.objects.filter(shpi=shpi, status_date__range=[before, timezone.now()])
        last_info = info.reverse()[:1].get  # last element
        abon = Abonents.objects.filter(shpi=shpi)[:1].get()
        fns = Abonents.objects.filter(shpi=shpi)[:1].get().fns_verbose
        context = {'Track_info': info, 'Track_last_info': last_info,
                   'Abonent': abon, 'Fnss': fns, }
        return render(request, 'track_shpi.html', context)


# Generate pdf for track shpi
@login_required()
def generate_pdf(request):
    if 'q' in request.GET:
        current_shpi = request.GET['q']
    # Model data
    before = timezone.now() - timezone.timedelta(days=60)  # 60 days before today
    info =      Status_history.objects.filter( shpi=current_shpi, status_date__range = [before, timezone.now()] )    
    last_info = Status_history.objects.filter( shpi=current_shpi, status_date__range = [before, timezone.now()] ).reverse()[:1].get # last element, в обр порядке
    abon = Abonents.objects.filter(shpi=current_shpi)[:1].get()
    fnss = Abonents.objects.filter(shpi=current_shpi)[:1].get().fns_verbose  # get fns_id
    context = { 'Track_info': info, 'Track_last_info': last_info, 'Abonent': abon, 'Fnss': fnss, }
    # Creating http response
    html_string = render_to_string('track_shpi_pdf.html', context)
    result = HTML(string=html_string).write_pdf(presentational_hints=True)
    response = HttpResponse(result, content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename={}'.format('sample.pdf')
    return response


@method_decorator(csrf_protect, name='dispatch')
class Statistics(LoginRequiredMixin, View):
    def get(self, request):
        form = StatisticsForm()
        return render(request, 'statistics.html', {'form': form})

    def post(self, request):
        form = StatisticsForm(request.POST)
        # if 'start_date' in request.POST:
        if form.is_valid():
            start_date_str = self.request.POST['start_date']
            end_date_str = self.request.POST['stop_date']
            context = self.get_context(start_date_str, end_date_str)
            return render(request, 'statistics_results.html', context)
        else:
            return HttpResponse(form.errors.values())


    def get_context(self, start_date_str, end_date_str):
        incorrect_date = False
        s_date = parse_date(start_date_str)
        e_date = parse_date(end_date_str)
        if s_date > e_date:  # incorrect dates
            incorrect_date = True
        # registered mails for the selected period
        zak = Abonents.objects.filter(record_creation_date__range=[s_date, e_date])
        # simple mails for the selected period
        simpl = OrdinaryMails.objects.filter(record_creation_date__range=[s_date, e_date])
        # Заказные отправления без увед
        zak_nu = zak.filter(notification_id='NU')
        # Заказные отправления с уведомлением
        zak_wu = zak.filter(notification_id='WU')
        # Заказные административные отправления с уведомл всего
        zak_adm = zak.filter(notification_id='AU')
        # С разбиением по налоговым:
        zak_list = []
        if self.request.user.username == 'admin':
            for q in Abonents.fns:
                zak_list.append([q[1],  # расшифровка налоговой
                                 simpl.filter(fns_id=q[0]).count(),
                                 zak_nu.filter(fns_id=q[0]).count(),
                                 zak_wu.filter(fns_id=q[0]).count(),
                                 zak_adm.filter(fns_id=q[0]).count(),
                                 q[0],  # fns_id
                                ]
                               )
        else:  # конкретная налговая
            fns_id = self.request.user.fns_id
            for q in Abonents.fns:
                if q[0] == fns_id:
                    zak_list.append([q[1],  # расшифровка налоговой
                                     simpl.filter(fns_id=fns_id).count(),
                                     zak_nu.filter(fns_id=fns_id).count(),
                                     zak_wu.filter(fns_id=fns_id).count(),
                                     zak_adm.filter(fns_id=fns_id).count(),
                                     fns_id,
                                    ]
                                   )
        context = {'kol': zak.count() + simpl.count(),
                   'kol_simpl': simpl.count(),
                   'kol_zak': zak_nu.count(),
                   'kol_zak_u': zak_wu.count(),
                   'kol_zak_adm': zak_adm.count(),
                   'start_date': start_date_str,
                   'end_date': end_date_str,
                   'zak_list': zak_list,
                   'incorrect_date': incorrect_date
                   }
        send_message('Просмотр статистики '
                     + self.request.user.username
                     + ' c '+start_date_str
                     + ' по '+end_date_str)
        return context


class Statistics_print(Statistics, View):
    def get(self, request):
        if 'start_date' in request.GET:
            start_date_str = self.request.GET['start_date']
            end_date_str = self.request.GET['end_date']
            context = self.get_context(start_date_str, end_date_str)
            html_string = render_to_string('statistics_print.html', context)
            result = HTML(string=html_string).write_pdf(presentational_hints=True)
            response = HttpResponse(result, content_type='application/pdf')
            response['Content-Disposition'] = 'inline; filename={}'.format('statistics.pdf')
            return response


@method_decorator(csrf_protect, name='dispatch')
class Detail_statistics(LoginRequiredMixin, View):
    def get(self, request):
        if 'start_date' in request.GET:
            start_date_str = self.request.GET['start_date']
            end_date_str = self.request.GET['stop_date']
            s_date = parse_date(start_date_str)
            e_date = parse_date(end_date_str)
            total = self.request.GET['total']
            fns_id = self.request.GET['fns_id']
            notification_id = self.request.GET['notification']
            if self.request.GET['print'] == '1':
                print_as_pdf = True
            else:
                print_as_pdf = False

            if notification_id != "OR":  # registered
                regs = Registers2.objects.filter(reg_date__range=[s_date, e_date],
                                                fns_id=fns_id,
                                                notification_id=notification_id)
                context = { 'start_date': start_date_str,
                            'end_date': end_date_str,
                            'fns_id': fns_id,
                            'fns': OrdinaryMails.fns_verbose_external_use(fns_id),
                            'regs': regs,
                            'total': total, }
                if print_as_pdf:
                    html_string = render_to_string('statistics_detail_results_print.html', context)
                    result = HTML(string=html_string).write_pdf(presentational_hints=True)
                    response = HttpResponse(result, content_type='application/pdf')
                    response['Content-Disposition'] = 'inline; filename={}'.format('statistics.pdf')
                    return response
                else:  # html-page
                    return render(request, 'statistics_detail_results.html', context)
            else:  # not registered mails
                simpl_mails = OrdinaryMails.objects.filter(record_creation_date__range=[s_date, e_date], fns_id=fns_id)
                context = { 'start_date': start_date_str,
                            'end_date': end_date_str,
                            'fns_id': fns_id,
                            'fns': OrdinaryMails.fns_verbose_external_use(fns_id),
                            'total': total,
                            'mails': simpl_mails, }
                return render(request, 'statistics_detail_simpl_results.html', context)
        else:
            return HttpResponse('<p>'+'Что-то пошло не так... '+'</p><a href="/myapp/add_registry/">Назад</a><a href="/myapp/"> Главная</a>')


@login_required()
def view_registers(request):
    if request.method == 'POST':
        form = ViewRegistersForm(request.POST)
        if form.is_valid():
            current_registry = form.cleaned_data['field']
            if bool(Registers2.objects.filter(id=current_registry).exists()):

                # pdf of notices
                if request.POST.get('var') == 'izv_pdf':
                    if os.path.exists('notices.pdf'):
                        os.remove('notices.pdf')
                    if Registers2.objects.get(id=current_registry).notification_id == 'OR':
                        return HttpResponse('<p>Для реестров простых отправлений данная функция не реализована.</p>  <a href="/myapp/view_registers/">Назад</a>')
                    # 'registry printed' flag
                    rg_in = Registers2.objects.filter(id=current_registry)[:1].get()
                    rg = Registers2(id=rg_in.id,
                                    reg_number=rg_in.reg_number,
                                    reg_date=rg_in.reg_date,
                                    reg_real_datetime=rg_in.reg_real_datetime,
                                    fns_id=rg_in.fns_id,
                                    notification_id=rg_in.notification_id,
                                    printed=True)
                    rg.save()
                    send_message('Напечатаны извещения pdf (реестр '+str(current_registry)+')')
                    # print pdf
                    abons = Abonents.objects.filter(reg_id=current_registry)
                    i = 0
                    all_abons = []
                    for q in abons:
                        i = i + 1
                        if i==1:
                            abons_0=None; abons_1=None; abons_2=None; abons_3=None
                            abons_0 = q
                        if i==2:
                            abons_1 = q
                        if i==3:
                            abons_2 = q
                        if i==4: 
                            abons_3 = q
                            all_abons.append([abons_0, abons_1, abons_2, abons_3])
                            i = 0
                    if i != 0:
                        all_abons.append([abons_0, abons_1, abons_2, abons_3])
                    today = timezone.now().date
                    uved = False
                    context = { 'abons':abons, 'all_abons':all_abons, 'today':today, 'media_path':settings.MEDIA_ROOT, 'uved':uved, }     
                    template = get_template("2_cols_2_rows.html")
                    html = template.render(context)
                    options = { "disable-local-file-access": None,
                                "enable-local-file-access": None,
                                "print-media-type": None,
                                "orientation": "Landscape",
                            }
                    pdf = pdfkit.from_string(html, False, options=options)
                    response = HttpResponse(pdf, content_type='application/pdf')
                    response['Content-Disposition'] = 'attachment; filename=notices.pdf'
                    return response

                # pdf of notifications
                if request.POST.get('var') == 'uved_pdf':
                    if os.path.exists('uvedoml.pdf'):
                        os.remove('uvedoml.pdf')
                    if Registers2.objects.get(id=current_registry).notification_id == 'OR':
                        return HttpResponse('<p>Для реестров простых отправлений данная функция не реализована.</p>  <a href="/myapp/view_registers/">Назад</a>')
                    # не делаю отметку о том, что реестр напечатан !
                    send_message('Напечатаны уведомления pdf (реестр '+str(current_registry)+')')
                    # print pdf
                    abons = Abonents.objects.filter(reg_id=current_registry)
                    i = 0
                    all_abons = []
                    for q in abons:
                        i = i + 1
                        if i==1:
                            abons_0=None; abons_1=None; abons_2=None; abons_3=None
                            abons_0 = q
                        if i==2:
                            abons_1 = q
                        if i==3:
                            abons_2 = q
                        if i==4:
                            abons_3 = q
                            all_abons.append([abons_0, abons_1, abons_2, abons_3])
                            i = 0
                    if i != 0:
                        all_abons.append([abons_0, abons_1, abons_2, abons_3])
                    today = timezone.now().date
                    uved = True
                    context = { 'abons':abons, 'all_abons':all_abons, 'today':today, 'media_path':settings.MEDIA_ROOT, 'uved':uved, }    #передаю значения в форму  
                    template = get_template("2_cols_2_rows.html")
                    html = template.render(context)
                    options = { "disable-local-file-access": None,
                                "enable-local-file-access": None,
                                "print-media-type": None,
                                "orientation": "Landscape",
                              }
                    pdf = pdfkit.from_string(html, False, options=options)
                    response = HttpResponse(pdf, content_type='application/pdf')
                    response['Content-Disposition'] = 'attachment; filename=uvedoml.pdf'
                    return response

                # xls of notices
                if request.POST.get('var') == 'izv':
                    # make backup of database once a day
                    if r.exists('last:print:datetime'):
                        last_print = datetime.strptime(r.get('last:print:datetime'), "%Y-%m-%d %H:%M:%S.%f" )
                        timedelta = datetime.now() - last_print
                        timedelta_hours = timedelta.days*24 + timedelta.seconds/3600
                        if timedelta_hours > 10:
                            copy(r'db.sqlite3', r'dbackup.bk')
                            last_print = r.set('last:print:datetime', str(datetime.now()))
                    else:
                        last_print = r.set('last:print:datetime', str(datetime.now())) 
                    send_message('Напечатаны извещения xls (реестр '+str(current_registry)+')')
                    result = generate_xls_file_for_izv_printing(current_registry)
                    return FileResponse(open(result,'rb'))

                # del selected registry
                if request.POST.get('var') == 'del':
                    Reg=Registers2.objects.filter(id = current_registry)
                    send_message('Удалён реестр '+str(current_registry))
                    Reg.delete()
                    return HttpResponse('<p>Реестр '+str(current_registry)+' удалён.</p>  <a href="/myapp/view_registers/">Назад</a>' )    

                # pdf of registers
                if request.POST.get('var') == 'pdf':
                    pdf = get_pdf_reg(current_registry)
                    with open(pdf, 'rb') as f:
                        file_data = f.read()
                    response = HttpResponse(file_data, content_type='application/pdf')
                    response['Content-Disposition'] = 'attachment; filename='+pdf
                    return response

                # xls of registers
                if request.POST.get('var') == 'xls':
                    filename = create_export_xls(current_registry)
                    return FileResponse(open(filename,'rb'))

            else:
                return HttpResponse('<p>'+'Нет такого реестра'+'</p><a href="/myapp/print_notice/">Назад  </a><a href="/myapp/">Главная</a>')        
        else:
            return HttpResponse('<p>'+'Что-то пошло не так... '+'</p><a href="/myapp/print_notices/">Назад  </a><a href="/myapp/">Главная</a>')            
    else:
        form = ViewRegistersForm()
        if request.user.username == 'admin':
            info = Registers2.objects.order_by('-id')
        else:
            info = Registers2.objects.order_by('-id').filter(fns_id=request.user.fns_id)
        # pagination:
        paginator = Paginator(info, 40)  # 40 registries per page
        page = request.GET.get('page', 1)  # number of page, 1 - start value
        regss = paginator.get_page(page)
        context = {'Registers_info': regss, 'form': form, 'page': page, }
        return render(request, 'view_registers.html', context)


@login_required()
def view_ordinary_registry(request, registry_id):
    if (request.method == 'GET'):  # and (request.user.username == 'admin'):
        mails = OrdinaryMails.objects.filter(reg_id__id=registry_id)
        registry_nmbr = mails[0].reg_id
        context = {'mails': mails, 'registry_id': registry_id, 'registry_nmbr': registry_nmbr, }
        return render(request, 'view_ordinary_reg.html', context)


@login_required()
def view_list_of_registers(request):
    if request.method == 'POST':
        pass
    else:
        form = ViewRegistersForm()
        if (request.user.username=='admin') and ('regs' in request.GET):
            info = Registers2.objects.order_by('-id').filter(notification_id__in=['NU','WU','AU'])
            regs_list = json.loads(request.GET['regs'])  # convert str to list
            info = info.filter(id__in=regs_list)
            return render(request, 'view_registers.html', {'Registers_info': info, 'form': form, 'page': 1, })
        else:
            return HttpResponse('<p>Что-то пошло не так...</p> <a href="/myapp/view_list_of_registers/">Назад</a>')


@login_required()
def view_registery_detail(request, register=55):
    if (Registers2.objects.filter(id=register).exists()):
        Reg = Registers2.objects.filter(id=register)[:1].get()
        abons = Abonents.objects.filter(reg_id=register)
        printed = False  # атрибут шаблона: ПЕЧАТЬ/ПРОСМОТР
        context = { 'abons':abons, 'Reg':Reg, 'printed':printed, }
        return render(request, 'print_registry.html', context)
    else:
        return HttpResponse('<p>'+'Нет такого реестра'+'</p><a href="/myapp/view_registers/">Назад  </a><a href="/myapp/">Главная</a>')         


class RegistryGroups(LoginRequiredMixin, View):
    def post(self, request):
        form = ViewRegistersForm(request.POST)
        numbers = request.POST.getlist('checkbox')

        # del selected registers
        if request.POST.get('var') == 'del':
            Reg  = Registers2.objects.filter(id__in = numbers)
            Reg.delete()
            send_message('Удалены реестры '+str(numbers))
            return HttpResponse('<p>Реестры '+str(numbers)+' удалены.</p>  <a href="/myapp/del_registers/">Назад</a>' )   

        # group of xls-files of notices (zip)
        if request.POST.get('var') =='izv':
            # make backup of database once a day (вынести в отдельную процедуру)
            if r.exists('last:print:datetime'):
                last_print = datetime.strptime(r.get('last:print:datetime'), "%Y-%m-%d %H:%M:%S.%f" )
                timedelta = datetime.now() - last_print
                timedelta_hours = timedelta.days*24 + timedelta.seconds/3600
                if timedelta_hours > 10:
                    copy(r'db.sqlite3', r'dbackup.bk')
                    last_print = r.set( 'last:print:datetime', str(datetime.now()) )
                    send_db_to_telegram();
                    send_message('Сделан бекап базы '+str(datetime.now()))
            else:
                last_print = r.set( 'last:print:datetime', str(datetime.now()) )
            try:
                # message to telegram
                send_message('Напечатана группа извещений xls: '+str(numbers))
                tmp = tempfile.NamedTemporaryFile(delete=True)
                tmp.name = 'REGS'+str(numbers)+'.zip'
                with open(tmp.name, 'w'):
                    write_izv_xls(numbers, tmp.name)  # write to temporary file
                    return FileResponse(open(tmp.name, 'rb'))
            finally:
                os.remove(tmp.name)
                delete_tmp_files()

        # group of registers in pdf files (zip)
        if request.POST.get('var') == 'reg_pdf':
            try:
                send_message('Напечатана группа реестров pdf: '+str(numbers))
                tmp = tempfile.NamedTemporaryFile(delete=True)
                tmp.name = 'REGS'+str(numbers)+'.zip'
                with open(tmp.name, 'w'):
                    write_reg_pdf(numbers, tmp.name)
                    return FileResponse(open(tmp.name, 'rb'))
            finally:
                os.remove(tmp.name)

        else:
            send_message('Что-то пошло не так при работе с группой извещений: '+str(numbers))
            return HttpResponse('<p>' + 'Что-то пошло не так... ' +
                                '</p><a href="/myapp/print_notices/">Назад  </a><a href="/myapp/">Главная</a>')

    def get(self, request):
        info = Registers2.objects.order_by('-id').filter(fns_id=request.user.fns_id)
        if request.user.username == 'admin':
            info = Registers2.objects.order_by('-id').all()
        # pagination:
        paginator = Paginator(info, 100)  # 100 registries per page
        page = request.GET.get('page',1)  # number of page, 1 - start value
        regss = paginator.get_page(page)
        context = {'Registers_info': regss, 'page': page, }
        return render(request, 'del_registers.html', context)


@login_required()
def search(request):
    if request.user.username == 'admin':
        if request.method == 'POST':
            fio = request.POST['fio']
            addr = request.POST['addr']
            reg_id = request.POST['reg_id']
            reg_nmbr = request.POST['reg_nmbr']
            start_date = request.POST['start_date']
            stop_date = request.POST['stop_date']
            # search by FIO & address
            if (fio!='' or addr!='') and (Abonents.objects.filter(address__contains=addr).exists() and Abonents.objects.filter(fio__contains=fio).exists() ):
                Abons = Abonents.objects.filter(fio__contains=fio).filter(address__contains=addr)
                context = {'Abons': Abons, }
                send_message('Поиск по ФИО/адр: '+fio+' '+addr)
                return render(request, 'search_results.html', context)
            # search by reg_id
            elif (reg_id!='') and (Registers2.objects.filter(id=reg_id).exists()):
                send_message('Поиск по reg_id: '+reg_id)
                return redirect('/myapp/view_registers/'+reg_id)
            # search by reg_number
            elif (reg_nmbr!='') and (Registers2.objects.filter(reg_number=reg_nmbr).exists()):
                regs = Registers2.objects.filter(reg_number=reg_nmbr).order_by('-id').values_list('id',flat=True).distinct()
                q = QueryDict(mutable=True)  # create QueryDict object
                q.__setitem__('regs', list(regs))  # put list of regs to QueryDict
                send_message('Поиск по reg_nmbr: '+reg_nmbr)
                return redirect('/myapp/view_list_of_registers/?'+q.urlencode())  # convert QueryDict to string of parans
            # search by date
            elif (start_date!='') and (stop_date!='') and (Registers2.objects.filter(reg_date__range=[start_date, stop_date]).exists()):
                regs = Registers2.objects.filter(reg_date__range=[start_date, stop_date]).order_by('-id').values_list('id',flat=True).distinct()
                q = QueryDict(mutable=True)  # create QueryDict object
                q.__setitem__('regs', list(regs))  # put list of regs to QueryDict
                send_message('Поиск по дате: '+start_date+' '+stop_date)
                return redirect('/myapp/view_list_of_registers/?'+q.urlencode())  # convert QueryDict to string of parans
            # else:
            else:
                return HttpResponse('<p>'+'Нет такого'+'</p><a href="/myapp/search/">Назад  </a><a href="/myapp/">Главная</a>')
        else:  # GET
            return render(request, 'search.html')


# REST API begin
# API must work only with token
class GetAbonentsInfoView(APIView):
    def get(self, request):
        fio = request.GET.get('fio')
        print(fio)
        queryset = Abonents.objects.filter(fio__contains=fio)
        # serialize extracted queryset
        serializer_for_queryset = AbonentsSerializer(
                instance=queryset,
                many=True  # на вход подаётся именно НАБОР записей
                )
        return Response(serializer_for_queryset.data)