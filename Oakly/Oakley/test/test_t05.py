from django.contrib.auth.models import User
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

# python manage.py test
class QuestionnaireSystemTest(StaticLiveServerTestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser123', password='hdhjdhjsh1234')
        self.browser = webdriver.Chrome()

    def tearDown(self):
        self.browser.quit()

    def test_questionnaire(self):
        self.browser.get(f"{self.live_server_url}")

        username_input = self.browser.find_element(By.NAME, 'username')
        password_input = self.browser.find_element(By.NAME, 'password')

        username_input.send_keys('testuser123')
        password_input.send_keys('hdhjdhjsh1234')
        password_input.send_keys(Keys.RETURN)

        time.sleep(5)

        monthly_income = self.browser.find_element(By.NAME, 'monthly_income')
        fixed_income = self.browser.find_element(By.ID, "fixed")
        rent = self.browser.find_element(By.ID, "rent")
        grocery = self.browser.find_element(By.ID, "grocery")
        savings = self.browser.find_element(By.ID, "savings")
        savings_goal = self.browser.find_element(By.NAME, 'savings_goal')
        regular = self.browser.find_element(By.ID, "regular")
        submit_button = self.browser.find_element(By.CLASS_NAME, "btn-success")

        monthly_income.send_keys('$10000')
        fixed_income.click()
        rent.click()
        grocery.click()
        savings.click()
        savings_goal.send_keys('$100000')

        time.sleep(2)

        self.browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

        regular.click()
        submit_button.click()

        time.sleep(5)

        self.browser.get(f"{self.live_server_url}/profile/")

        time.sleep(2)

        self.assertEqual(self.browser.current_url, f"{self.live_server_url}/profile/")