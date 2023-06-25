from django.test import TestCase
from myapp.models import Registers2
from django.utils import timezone


class Registers2ModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        Registers2.objects.create(reg_number=1, notification_id='NU')

    def reg_number_label(self):
        reg = Registers2.objects.get(id=1)
        field_label = reg._meta.get_field('reg_number').verbose_name
        self.assertEqual(field_label, 'reg_number')

    def test_fns_id_max_length(self):
        reg = Registers2.objects.get(id=1)
        max_length = reg._meta.get_field('fns_id').max_length
        self.assertEqual(max_length, 2)

    def test_reg_date_date(self):
        reg = Registers2.objects.get(id=1)
        self.assertEqual(reg.reg_date, timezone.now().date())

    def test_object_name(self):
        reg = Registers2.objects.get(id=1)
        expected_object_name = reg.reg_number
        self.assertEqual(str(reg), str(expected_object_name))

