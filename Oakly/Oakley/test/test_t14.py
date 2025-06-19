from django.contrib.auth.models import User
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

# python manage.py test
class FinancialAdvisorSignUpSystemTest(StaticLiveServerTestCase):
    def setUp(self):
        self.browser = webdriver.Chrome()

    def tearDown(self):
        self.browser.quit()

    def test_advisor_signup(self):
        self.browser.get(f"{self.live_server_url}/advisor/signup/")
        time.sleep(2)

        self.browser.find_element(By.NAME, "firstName").send_keys("John")
        self.browser.find_element(By.NAME, "lastName").send_keys("Doe")
        self.browser.find_element(By.NAME, "phoneNumber").send_keys("123-456-7890")
        self.browser.find_element(By.NAME, "email").send_keys("johndoe@example.com")
        self.browser.find_element(By.NAME, "username").send_keys("johndoe123")
        self.browser.find_element(By.NAME, "password").send_keys("securePassword1")
        self.browser.find_element(By.NAME, "confirmPassword").send_keys("securePassword1")
        self.browser.find_element(By.NAME, "confirmPassword").send_keys(Keys.RETURN)

        time.sleep(2)

        self.assertEqual(self.browser.current_url, f"{self.live_server_url}/advisor/questionnaire/")

    def test_advisor_signup_mismatch_password(self):
        self.browser.get(f"{self.live_server_url}/advisor/signup/")
        time.sleep(2)

        self.browser.find_element(By.NAME, "firstName").send_keys("John")
        self.browser.find_element(By.NAME, "lastName").send_keys("Doe")
        self.browser.find_element(By.NAME, "phoneNumber").send_keys("123-456-7890")
        self.browser.find_element(By.NAME, "email").send_keys("johndoe@example.com")
        self.browser.find_element(By.NAME, "username").send_keys("johndoe123")
        self.browser.find_element(By.NAME, "password").send_keys("securePassword1")
        self.browser.find_element(By.NAME, "confirmPassword").send_keys("password1")
        self.browser.find_element(By.NAME, "confirmPassword").send_keys(Keys.RETURN)

        time.sleep(2)

        self.assertEqual(self.browser.current_url, f"{self.live_server_url}/advisor/signup/")