from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from Oakley.models import Transaction

# python manage.py test
class AddTransactionViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.login(username='testuser', password='testpass')

    def test_add_transaction(self):
        data = {
            "date": "2025-04-05",
            "category": "Groceries",
            "merchant": "Costco",
            "amount": "75.50",
            "payment_method": "Debit",
            "location": "New Jersey",
            "transaction_type" : "expense"
        }
        response = self.client.post(reverse('Oakley:add_transaction'), data)
        self.assertEqual(response.status_code, 302)

        txn = Transaction.objects.first()
        self.assertIsNotNone(txn)
        self.assertEqual(txn.category, "Groceries")
        self.assertEqual(txn.user, self.user)