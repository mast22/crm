from django.test import Client, TestCase
from common.preload import run_preload


class BaseTaskTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        run_preload(add_users=True)

    def setUp(self):
        self.client = Client()