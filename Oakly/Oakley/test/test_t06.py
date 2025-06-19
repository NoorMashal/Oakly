from gettext import translation

from django.contrib.auth.models import User
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
from Oakley.models import Transaction, Profile


# python manage.py test
class ViewTransactionsSystemTest(StaticLiveServerTestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='user6', password='password6')
        self.profile1 = Profile.objects.create(
            user=self.user,
            monthly_income=5000,
            income_stability='Stable',
            recurring_bills='Rent, Utilities',
            variable_spending='Groceries, Entertainment',
            primary_goal='Save for emergency fund',
            savings_goal=10000,
            expense_tracking='Using budgeting app'
        )
        self.profile1.save()

        self.transaction1 = Transaction.objects.create(
            user=self.user,
            category='Groceries',
            merchant='Whole Foods',
            amount=45.99,
            payment_method='Credit',
            location='New York',
            transaction_type='expense'
        )
        self.transaction1.save()

        self.transaction2 = Transaction.objects.create(
            user=self.user,
            category='Groceries',
            merchant='ShopRite',
            amount=75.50,
            payment_method='Debit',
            location='Maryland',
            transaction_type='expense'
        )
        self.transaction2.save()

        self.transaction3 = Transaction.objects.create(
            user=self.user,
            category='Entertainment',
            merchant='AMC Movie Theaters',
            amount=100.00,
            payment_method='Credit',
            location='California',
            transaction_type='expense'
        )
        self.transaction3.save()

        self.browser = webdriver.Chrome()

    def tearDown(self):
        self.browser.quit()

    def test_view_transactions(self):
        self.browser.get(f"{self.live_server_url}")

        username_input = self.browser.find_element(By.NAME, 'username')
        password_input = self.browser.find_element(By.NAME, 'password')

        username_input.send_keys('user6')
        password_input.send_keys('password6')
        password_input.send_keys(Keys.RETURN)

        time.sleep(2)

        self.browser.get(f"{self.live_server_url}/home/")

        self.browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(5)

        transaction_rows = self.browser.find_elements(By.CSS_SELECTOR, "table.table tbody tr")
        self.assertEqual(len(transaction_rows), 3)