from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from Oakley.models import Profile

class QuestionnaireSQLInjectionTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.client.login(username='testuser', password='password')

    #Inject a SQL injection payload that tries to manipulate the numeric conversion or cause issues in the query.
    def test_sql_injection_in_primary_goal(self):
        response = self.client.post(reverse('Oakley:questionnaire'), {
            'monthly_income': '3000',
            'income_stability': 'stable',
            'recurring_bills': ['rent', 'utilities'],
            'variable_spending': ['groceries', 'entertainment'],
            'primary_goal': "' OR '1'='1",
            'savings_goal': '4000',
            'expense_tracking': 'yes',
        })
        self.assertEqual(response.status_code, 302)  # Should redirect
        self.assertTrue(Profile.objects.filter(user=self.user).exists())

    #This SQL injection tries to the profile table
    def test_sql_injection_in_recurring_bills(self):
        response = self.client.post(reverse('Oakley:questionnaire'), {
            'monthly_income': '4000',
            'income_stability': 'stable',
            'recurring_bills': ["rent", "utilities", "'; DROP TABLE Profile; --"],
            'variable_spending': ["groceries", "'; DROP TABLE Profile; --"],
            'primary_goal': 'Save more',
            'savings_goal': '5000',
            'expense_tracking': 'yes',
        })
        self.assertEqual(response.status_code, 302)  # Should redirect
        self.assertTrue(Profile.objects.filter(user=self.user).exists())