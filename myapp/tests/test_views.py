from django.test import TestCase
from django.urls import reverse
from myapp.models import Registers2
from myapp.models import CustomUser
from django.test.client import Client
# import unittest


class RegisterListViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create 13 registers for pagination tests
        number_of_regs = 13
        for reg_id in range(number_of_regs):
            Registers2.objects.create(
                reg_number=reg_id,
                fns_id='OK',
                notification_id='OR',
            )
        self.client = Client()
        self.user = User.objects.create_user('john', 'lennon@thebeatles.com', 'johnpassword')


    def test_login_view_url_exists_at_desired_location(self):
        response = self.client.get('/login/')
        self.assertEqual(response.status_code, 200)


    def test_view_registers_url_exists_at_desired_location(self):
        response = self.client.get('/view_registers/')
        print(response)
        self.assertEqual(response.status_code, 200)

    """
    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('authors'))
        self.assertEqual(response.status_code, 200)
    """
    """
        def test_pagination_is_ten(self):
        response = self.client.get('/myapp/view_registers/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('is_paginated' in response.context)
        self.assertTrue(response.context['is_paginated'] == True)
        self.assertEqual(len(response.context['author_list']), 10)

    def test_lists_all_registers(self):
        # Get second page and confirm it has (exactly) remaining 3 items
        response = self.client.get(reverse('authors')+'?page=2')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('is_paginated' in response.context)
        self.assertTrue(response.context['is_paginated'] == True)
        self.assertEqual(len(response.context['author_list']), 3)
    """
