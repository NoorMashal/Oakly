from django.contrib.auth.models import User
from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

class AdminAccessTest(LiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.browser = webdriver.Chrome()

    @classmethod
    def tearDownClass(cls):
        cls.browser.quit()
        super().tearDownClass()

    def setUp(self):
        self.admin = User.objects.create_superuser(
            username='admin', email='admin@example.com', password='adminpass'
        )

        self.customer = User.objects.create_user(
            username='customer', email='customer@example.com', password='custpass'
        )

    def login_and_test_admin_access(self, username, password, expect_success):
        self.browser.get(self.live_server_url + "/admin/")
        time.sleep(1)
        username_input = self.browser.find_element(By.NAME, "username")
        password_input = self.browser.find_element(By.NAME, "password")

        username_input.send_keys(username)
        password_input.send_keys(password)
        password_input.send_keys(Keys.RETURN)
        time.sleep(1)

        if expect_success:
            self.assertIn("Site administration", self.browser.page_source)
        else:
            self.assertIn("Please enter the correct username and password", self.browser.page_source)

        # Logout if login was successful
        if expect_success:
            self.browser.get(self.live_server_url + "/admin/logout/")
            time.sleep(1)

    def test_admin_access_wrong_password(self):
        self.login_and_test_admin_access("admin", "wrongpass", expect_success=False)

    def test_admin_access_correct_password(self):
        self.login_and_test_admin_access("admin", "adminpass", expect_success=True)

    def test_customer_admin_access(self):
        self.login_and_test_admin_access("customer", "custpass", expect_success=False)

    def test_advisor_admin_access(self):
        self.login_and_test_admin_access("advisor", "advisepass", expect_success=False)
