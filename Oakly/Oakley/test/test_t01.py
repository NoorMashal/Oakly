from django.contrib.auth.models import User
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

# python manage.py test
class CustomerLoginSystemTest(StaticLiveServerTestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.browser = webdriver.Chrome()

    def tearDown(self):
        self.browser.quit()

    def test_customer_login(self):
        self.browser.get(f"{self.live_server_url}")

        username_input = self.browser.find_element(By.NAME, 'username')
        password_input = self.browser.find_element(By.NAME, 'password')

        username_input.send_keys('testuser')
        password_input.send_keys('testpass')
        password_input.send_keys(Keys.RETURN)

        time.sleep(2)

        self.assertEqual(self.browser.current_url, f"{self.live_server_url}/questionnaire/")

    def test_incorrect_customer_login(self):
        self.browser.get(f"{self.live_server_url}")

        username_input = self.browser.find_element(By.NAME, 'username')
        password_input = self.browser.find_element(By.NAME, 'password')

        username_input.send_keys('wrong')
        password_input.send_keys('password')
        password_input.send_keys(Keys.RETURN)

        time.sleep(2)

        self.assertEqual(self.browser.current_url, f"{self.live_server_url}")