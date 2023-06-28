from django import forms
from django.core.validators import EMPTY_VALUES
from django.forms import ModelForm, CharField, TextInput
from django.core.exceptions import ValidationError
from django.forms.fields import ChoiceField
from .models import Status_history, CustomUser, Registers2, Abonents
from django.contrib.auth.forms import UserCreationForm
from datetime import datetime
from .widgets import DatePickerInput
from django.core.exceptions import ValidationError


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm):
        model = CustomUser
        fields = ('username', 'email', 'fns_id')


class CustomUserChangeForm(UserCreationForm):
    class Meta(UserCreationForm):
        model = CustomUser
        fields = ('username', 'email', 'fns_id')


class PostForm(ModelForm):
    class Meta:
        model = Abonents  # модель, поля к-рой исп для создания формы
        fields = ('shpi', 'fns_id', 'record_creation_date')


class Request_Track_Form(forms.Form):
    shpi = forms.CharField(max_length=16, label='Идентификатор')


class Generate_SHPI_Form(forms.Form):
    col = CharField(widget=TextInput(attrs={'type': 'number'}),
                    max_length=6,
                    label='Введите количество ШПИ')


class Login_Form(forms.Form):
    user = CharField(max_length=20, label='Логин')
    passwd = CharField(max_length=20,
                       label='Пароль',
                       widget=forms.PasswordInput)


class UploadRegistryForm(forms.Form):
    file = forms.FileField(label='Файл:')
    choise_field = forms.ChoiceField(widget=forms.Select(),
                                     choices=Registers2.notification,
                                     required=True,
                                     label='Присвоить статус отправлениям:')


class ChooseYearForUploadRegistryFormAdmin(forms.Form):
    registry_years = ''
    choise_registry_year = forms.ChoiceField(widget=forms.Select(),
                                             required=False,
                                             choices=registry_years,
                                             label='Год реестра:') 
    choise_value = (('новый', 'новый'), ('существующий', 'существующий'))
    registry = forms.ChoiceField(widget=forms.Select(),
                                 required=False,
                                 choices=choise_value,
                                 initial=choise_value[0],
                                 label='Реестр:')


class UploadRegistryFormAdmin(forms.Form):
    file = forms.FileField(label='Файл:')
    choise_field = forms.ChoiceField(widget=forms.Select(),
                                     choices=Registers2.notification,
                                     required=True,
                                     label='Присвоить статус отправлениям:')
    choise_ifns = forms.ChoiceField(widget=forms.Select(),
                                    choices=Registers2.fns,
                                    required=True,
                                    label='От имени:')
    t = ''
    choise_registry = forms.CharField(required=False,
                                      widget=forms.Select(choices=t),
                                      label='Номер реестра:')


class UploadScanForm(forms.Form):
    file = forms.FileField(label='Файл:')
    ch_field = forms.ChoiceField(widget=forms.Select(),
                                 choices=Status_history.status,
                                 required=True,
                                 label='Присвоить статус:')


class ViewRegistersForm(forms.Form):
    field = CharField(max_length=10, label='Id реестра')


class AddOrdinaryMailFormAdmin(forms.Form):
    choise_ifns = forms.ChoiceField(widget=forms.Select(),
                                    choices=Registers2.fns,
                                    required=True,
                                    label='От имени:')


class StatisticsForm(forms.Form):
    start_date = forms.DateField(widget=DatePickerInput, label='Вывести статистику начиная с')
    stop_date = forms.DateField(widget=DatePickerInput, label='... по дату')

    def clean(self):  # _dates
        cleaned_data = super().clean() 
        start_date = cleaned_data.get('start_date')
        stop_date = cleaned_data.get('stop_date')
        if start_date > stop_date:
            raise ValidationError('Даты выбраны неверно: начальная дата позже конечной')
        # always must return the cleaned data.
        return cleaned_data
