
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser  # User


# model to replace the regular User model with the addition of custom field fns_id
class CustomUser(AbstractUser):
    fns_id = models.CharField(max_length=2, default='LN')

    def __str__(self):
        return self.username


class Registers2(models.Model):
    OK = 'OK'  # 'октябрьская'
    ZD = 'ZD'  # 'железнодорожная'
    LN = 'LN'  # 'ленинская'
    ZR = 'ZR'  # 'зареченская'
    PM = 'PM'  # 'первомайская'
    PO = 'PO'  # 'гл. упр. по Пенз. обл.'
    PS = 'PS'  # 'ПензаСтат'
    fns = ((OK, 'ИФНС России по Октябрьскому району г. Пензы'),
           (ZD, 'ИФНС России по Железнодорожному району г. Пензы'),
           (LN, 'ИФНС России по Ленинскому району г. Пензы'),
           (ZR, 'ИФНС России по г. Заречному Пензенской области'),
           (PM, 'ИФНС России по Первомайскому району г. Пензы'),
           (PO, 'УФНС России по Пензенской области'),
           (PS, 'Территориальный орган Федеральной службы государственной статистики по Пензенской области'),
          )

    notification = ((None, ''),
                    ('OR', 'простое'),
                    ('NU', 'заказное'),
                    ('WU', 'заказное с уведомлением'),
                    ('AU', 'административное заказное с уведомлением'),
                    )
    notif_rodit_padezh = (('OR', 'простых'),
                          ('NU', 'заказных'),
                          ('WU', 'заказных с уведомлением'),
                          ('AU', 'административных заказных с уведомлением'),
                         )
    reg_number = models.PositiveBigIntegerField()  # НЕУНИКАЛЬНЫЙ номер реестра для отображения
    reg_date = models.DateField(default=timezone.now)
    reg_real_datetime = models.DateTimeField(default=timezone.now)
    fns_id = models.CharField(max_length=2, choices=fns)
    notification_id = models.CharField(max_length=2, choices=notification)
    printed = models.BooleanField(default=False)

    def __str__(self):
        return str(self.reg_number)

    def notification_verbose(self):  # расшифровка типа отправления
        return dict(Abonents.notification)[self.notification_id]

    def notification_verbose_rp(self):  # расшифровка в родительном падеже
        return dict(Abonents.notif_rodit_padezh)[self.notification_id]

    def fns_verbose(self):  # расшифровка фнс
        return dict(Generated_shpi.fns)[self.fns_id]

    def kol_mails(self):  # кол-во отправлений в реестре
        if self.notification_id == 'OR':
            return OrdinaryMails.objects.filter(reg_id=self.id).count()
        else:
            return Abonents.objects.filter(reg_id=self.id).count()

    def reg_year(self):
        return self.reg_date.year

    def years_list():
        '''За какие года существуют реестры'''
        years_list = set(Registers2.objects.all().values_list('reg_date__year'))
        return list(years_list)

    def year_reg_number(self):
        return str(self.reg_year())+'/'+str(self.reg_number)

    """ def get_absolute_url(self):
        return reverse('view_registers', args=[str(self.id)]) """

    class Meta:
        ordering = ["id"]


class OrdinaryMails(models.Model):
    record_creation_date = models.DateField(default=timezone.now)
    fns_id = models.CharField(max_length=2, choices=Registers2.fns)
    address = models.CharField(max_length=255, default='')
    fio = models.CharField(max_length=255, default='')
    made_date = models.CharField(max_length=128, blank=True, null=True)  # date of transfer
    doc_number = models.CharField(max_length=255, default='')
    inspector = models.CharField(max_length=30, default='')
    reg_id = models.ForeignKey(Registers2, to_field='id', on_delete=models.CASCADE, default=1)
    # reg_id = models.IntegerField(default=8)
    abon_id = models.CharField(max_length=40, default='')

    def __str__(self):
        return str(self.record_creation_date)

    def fns_verbose(self):
        return dict(Generated_shpi.fns)[self.fns_id]

    def fns_verbose_external_use(fns_id):
        return dict(Generated_shpi.fns)[fns_id]

    def notification_verbose(self):
        return 'простое'

    def reg_nmbr(self):
        return self.reg_id.reg_number

    def reg_idd(self):
        return self.reg_id.id

    class Meta:
        ordering = ["record_creation_date"]


class Abonents(models.Model):  # list of registered mails
    shpi = models.CharField(max_length=14, unique=True)  # unique=True, primary_key=True
    abon_id = models.CharField(max_length=40)
    fio = models.CharField(max_length=255)
    doc_number = models.CharField(max_length=255)
    made_date = models.CharField(max_length=128, blank=True, null=True)
    address = models.CharField(max_length=255, default='')
    telephone = models.CharField(max_length=12)
    inspector = models  .CharField(max_length=30, default='')
    notification_id = models.CharField(max_length=2, choices=Registers2.notification)
    record_creation_date = models.DateField(default=timezone.now)
    # id = models.ForeignKey(Registers2, to_field='id', on_delete=models.CASCADE)  # удалил id
    reg_id = models.ForeignKey(Registers2, to_field='id', on_delete=models.CASCADE)
    fns = Registers2.fns
    idd = models.AutoField(unique=True, primary_key=True)
    # idd = models.IntegerField(default=0)  # подготовка pk: AutoField(primary_key=True, unique=True,)

    notification = Registers2.notification
    notification_verbose = Registers2.notification_verbose
    notif_rodit_padezh = Registers2.notif_rodit_padezh
    fns_id = models.CharField(max_length=2, choices=Registers2.fns, default='')

    def __str__(self):
        return self.shpi

    def notification_verbose(self):
        return dict(Abonents.notification)[self.notification_id]

    def fns_verbose(self):
        return dict(Abonents.fns)[self.fns_id]


class Generated_shpi(models.Model):  # already generated SHPI's
    # shpi = models.OneToOneField(Abonents, to_field='shpi', on_delete=models.CASCADE, primary_key=True, unique=True)  # db_index=True - ндексировать поле для ускорения поиска
    shpi = models.IntegerField(primary_key=True, unique=True)
    generated_date = models.DateField(default=timezone.now)
    fns_id = models.CharField(max_length=2, choices=Registers2.fns)
    fns = Registers2.fns

    def __str__(self):
        return self.shpi

    def generate_shpi(self):
        self.generated_date = timezone.now()
        self.save()

    def fns_verbose(self):  # расшифровка фнс
        return dict(Generated_shpi.fns)[self.fns_id]


class Status_history(models.Model):  # status of mails
    shpi = models.ForeignKey(Abonents, to_field='shpi', on_delete=models.CASCADE)
    status_date = models.DateField()
    status = [('VR', 'вручено'),
              ('OB', 'в обработке'),
              ('PR', 'принят в отделении связи'),
              ('DO', 'доставка'),
              ('HR', 'хранение'),
              ('VZ', 'возврат'),
              ]
    status_id = models.CharField(max_length=2, choices=status, default='VZ')

    def status_verbose(self):
        return dict(Status_history.status)[self.status_id]

    def __str__(self):
        return self.shpi

    class Meta:
        ordering = ["status_date"]
