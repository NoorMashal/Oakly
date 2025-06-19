from django.test import TestCase
from django.contrib.auth.models import User
from Oakley.models import Transaction

# Run with: python manage.py test
class TransactionModelCase(TestCase):
    def test_str_representation(self):
        user = User.objects.create_user(username='testuser', password='testpass')
        txn = Transaction.objects.create(
            user=user,
            category='Groceries',
            merchant='Whole Foods',
            amount=45.99,
            payment_method='Credit',
            location='New York',
            transaction_type='expense'
        )
        expected_str = "Groceries, Whole Foods, 45.99, expense, Credit, New York"
        self.assertEqual(str(txn), expected_str)