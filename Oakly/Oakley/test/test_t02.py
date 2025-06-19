from django.contrib.auth.models import User, Group
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
from Oakley.models import FinancialAdvisorProfile

# python manage.py test
class FinancialAdvisorLoginSystemTest(StaticLiveServerTestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='advisor', password='testpass')
        self.user.backend = 'django.contrib.auth.backends.ModelBackend'
        self.group, _ = Group.objects.get_or_create(name="Financial Advisor")
        self.user.groups.add(self.group)

        self.financial_advisor_profile = FinancialAdvisorProfile.objects.create(
            user=self.user,
            first_name='John',
            last_name='Smith',
            phone_number='656-887-9080',
        )
        self.financial_advisor_profile.save()

        self.browser = webdriver.Chrome()

    def tearDown(self):
        self.browser.quit()

    def test_advisor_login(self):
        self.browser.get(f"{self.live_server_url}")

        username_input = self.browser.find_element(By.NAME, 'username')
        password_input = self.browser.find_element(By.NAME, 'password')

        username_input.send_keys('advisor')
        password_input.send_keys('testpass')
        password_input.send_keys(Keys.RETURN)

        time.sleep(2)

        self.assertEqual(self.browser.current_url, f"{self.live_server_url}/advisor/questionnaire/")

    def test_incorrect_advisor_login(self):
        self.browser.get(f"{self.live_server_url}")

        username_input = self.browser.find_element(By.NAME, 'username')
        password_input = self.browser.find_element(By.NAME, 'password')

        username_input.send_keys('wrong')
        password_input.send_keys('testpass')
        password_input.send_keys(Keys.RETURN)

        time.sleep(2)

        self.assertEqual(self.browser.current_url, f"{self.live_server_url}")