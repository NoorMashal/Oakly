from django.contrib.auth.models import User, Group
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
from Oakley.models import FinancialAdvisorProfile, Meetings


# python manage.py test
class FeedbackSystemTest(StaticLiveServerTestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='user8', password='password123')
        self.advisor_user = User.objects.create_user(username='advisor8', password='testpass8')
        self.advisor_user.backend = 'django.contrib.auth.backends.ModelBackend'
        self.group, _ = Group.objects.get_or_create(name="Financial Advisor")
        self.advisor_user.groups.add(self.group)

        self.financial_advisor_profile = FinancialAdvisorProfile.objects.create(
            user=self.advisor_user,
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

        self.meetings = Meetings.objects.create(
            advisor=self.financial_advisor_profile,
            user=self.user,
            day_of_week="Monday",
            start_time="9:30:00",
            end_time="14:30:00",
            status="upcoming",
            call_url="https://www.rocketmoney.com/",
            date="2025-04-20"
        )
        self.meetings.save()

        self.browser = webdriver.Chrome()

    def tearDown(self):
        self.browser.quit()

    def test_schedule_meeting(self):
        self.browser.get(f"{self.live_server_url}")

        username_input = self.browser.find_element(By.NAME, 'username')
        password_input = self.browser.find_element(By.NAME, 'password')

        username_input.send_keys('advisor8')
        password_input.send_keys('testpass8')
        password_input.send_keys(Keys.RETURN)
        time.sleep(3)

        self.browser.get(f"{self.live_server_url}/advisor/meetings")
        time.sleep(3)

        complete_button = self.browser.find_element(By.XPATH, "//button[text()='Complete']")
        complete_button.click()
        time.sleep(3)

        give_feedback_button = self.browser.find_element(By.LINK_TEXT, "Give Feedback")
        give_feedback_button.click()
        time.sleep(3)

        textarea = self.browser.find_element(By.NAME, "content")
        textarea.clear()
        textarea.send_keys("Great meeting! I learned a lot.")
        time.sleep(3)

        submit_btn = self.browser.find_element(By.XPATH, "//button[text()='Submit Feedback']")
        submit_btn.click()
        time.sleep(3)

        button_exists = len(self.browser.find_elements(By.XPATH, "//a[contains(text(), 'Edit Feedback')]")) > 0
        self.assertTrue(button_exists, "Edit Feedback button should exist on the page")