from django.contrib.auth.models import User, Group
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
from Oakley.models import FinancialAdvisorProfile, Availability


# python manage.py test
class MeetingSystemTest(StaticLiveServerTestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='user7', password='password123')
        self.financial_advisor_user = User.objects.create_user(username='advisor7', password='testpass7')
        self.financial_advisor_user.backend = 'django.contrib.auth.backends.ModelBackend'
        self.group, _ = Group.objects.get_or_create(name="Financial Advisor")
        self.financial_advisor_user.groups.add(self.group)

        self.financial_advisor_profile = FinancialAdvisorProfile.objects.create(
            user=self.financial_advisor_user,
            first_name='John',
            last_name='Smith',
            phone_number='656-887-9080',
            firm_name='Smith Financial Services LLC',
            certifications='CFP, CFA',
            experience_years=10,
            bio='John Smith is a trusted financial advisor with years of experience helping clients build wealth, plan for retirement, and reach financial goals.',
            specialties='Financial Planning, Investments, Retirement, Financial Services',
            website='https://www.rocketmoney.com/',
            linkedin='https://www.rocketmoney.com/',
            location='New York City, NY',
        )
        self.financial_advisor_profile.save()

        self.availability = Availability.objects.create(
            advisor=self.financial_advisor_profile,
            day_of_week='Monday',
            start_time="9:30:00",
            end_time="14:30:00"
        )
        self.availability.save()

        self.browser = webdriver.Chrome()

    def tearDown(self):
        self.browser.quit()

    def test_schedule_meeting(self):
        self.browser.get(f"{self.live_server_url}")

        username_input = self.browser.find_element(By.NAME, 'username')
        password_input = self.browser.find_element(By.NAME, 'password')

        username_input.send_keys('user7')
        password_input.send_keys('password123')
        password_input.send_keys(Keys.RETURN)

        time.sleep(3)

        self.browser.get(f"{self.live_server_url}/schedule/")
        time.sleep(3)

        username = 'advisor7'
        button = self.browser.find_element(By.CSS_SELECTOR, f"button[data-bs-target='#modal-{username}']")
        button.click()
        time.sleep(3)

        radio = self.browser.find_element(By.XPATH,"//input[@id='radio1']")
        radio.click()
        time.sleep(3)

        button2 = self.browser.find_element(By.ID, "confirm-button")
        button2.click()
        time.sleep(3)

        self.browser.get(f"{self.live_server_url}/meetings/")
        time.sleep(3)

        join_button = self.browser.find_element(By.LINK_TEXT, "Join Meeting")
        join_button.click()
        time.sleep(5)

        tabs = self.browser.window_handles
        self.browser.switch_to.window(tabs[1])
        time.sleep(5)

        self.assertTrue(self.browser.current_url.startswith("https://meet.jit.si/"))
