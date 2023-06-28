import datetime
from django.test import TestCase
from django.utils import timezone
from myapp.forms import UploadRegistryFormAdmin


class UploadRegistryFormAdminTest(TestCase):
    def test_file_field_label(self):
        form = UploadRegistryFormAdmin()
        self.assertTrue(form.fields['file'].label is None or form.fields['file'].label == 'Файл:')

    """
    def test_renew_form_date_in_past(self):
        date = datetime.date.today() - datetime.timedelta(days=1)
        form = RenewBookForm(data={'renewal_date': date})
        self.assertFalse(form.is_valid()) """
