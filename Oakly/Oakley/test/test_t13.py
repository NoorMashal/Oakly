from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

# python manage.py test
class CustomerSignUpSystemTest(StaticLiveServerTestCase):
    def setUp(self):
        self.browser = webdriver.Chrome()

    def tearDown(self):
        self.browser.quit()

    def test_customer_signup(self):
        self.browser.get(f"{self.live_server_url}/signup/")
        time.sleep(2)

        self.browser.find_element(By.NAME, "username").send_keys("testuser")
        self.browser.find_element(By.NAME, "email").send_keys("test@example.com")
        self.browser.find_element(By.NAME, "password1").send_keys("strongpassword123")
        self.browser.find_element(By.NAME, "password2").send_keys("strongpassword123")
        self.browser.find_element(By.NAME, "password2").send_keys(Keys.RETURN)

        time.sleep(2)

        self.assertEqual(self.browser.current_url, f"{self.live_server_url}/questionnaire/")

    def test_customer_signup_weak_password(self):
        self.browser.get(f"{self.live_server_url}/signup/")
        time.sleep(2)

        self.browser.find_element(By.NAME, "username").send_keys("testuser")
        self.browser.find_element(By.NAME, "email").send_keys("test@example.com")
        self.browser.find_element(By.NAME, "password1").send_keys("s")
        self.browser.find_element(By.NAME, "password2").send_keys("s")
        self.browser.find_element(By.NAME, "password2").send_keys(Keys.RETURN)

        time.sleep(2)

        self.assertEqual(self.browser.current_url, f"{self.live_server_url}")
