from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now
from django.utils.crypto import get_random_string


# Create your models here.
class Transaction(models.Model):
    TRANSACTION_TYPES = (
        ('income', 'Income'),
        ('expense', 'Expense'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(default=now)
    category = models.CharField(max_length=100)
    merchant = models.CharField(max_length=100)
    amount = models.FloatField(default=0.0)
    payment_method = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    transaction_type = models.CharField(max_length=7, choices=TRANSACTION_TYPES, default='expense')  # NEW

    def __str__(self):
        return f"{self.category}, {self.merchant}, {self.amount}, {self.transaction_type}, {self.payment_method}, {self.location}"


class Profile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    monthly_income = models.FloatField(default=0)
    income_stability = models.CharField(max_length=1000)
    recurring_bills = models.CharField(max_length=1000)
    variable_spending = models.CharField(max_length=1000)
    primary_goal = models.CharField(max_length=1000)
    savings_goal = models.FloatField(default=0)
    expense_tracking = models.CharField(max_length=1000)

    def __str__(self):
        return f"monthly income:{self.monthly_income}, income stability:{self.income_stability}, recurring bills:{self.recurring_bills}, variable spending:{self.variable_spending}, primary goal:{self.primary_goal}, savings goal:{self.savings_goal}, expense tracking:{self.expense_tracking}"


class FinancialAdvisorProfile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=100)
    firm_name = models.CharField(max_length=255, blank=True, null=True)
    certifications = models.TextField(blank=True, null=True)
    experience_years = models.IntegerField(default=0)
    bio = models.TextField(blank=True, null=True)
    specialties = models.TextField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    linkedin = models.URLField(blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)


class Availability(models.Model):
    advisor = models.ForeignKey(FinancialAdvisorProfile, on_delete=models.CASCADE, related_name='availabilities')
    day_of_week = models.CharField(max_length=9, choices=[
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
        ('Saturday', 'Saturday'),
        ('Sunday', 'Sunday'),
    ])
    start_time = models.TimeField()
    end_time = models.TimeField()

    class Meta:
        unique_together = ('advisor', 'day_of_week', 'start_time', 'end_time')




class Meetings(models.Model):
    STATUS_CHOICES = [
        ('upcoming', 'Upcoming'),
        ('completed', 'Completed'),
        ('canceled', 'Canceled'),
    ]

    advisor = models.ForeignKey(FinancialAdvisorProfile, on_delete=models.CASCADE, related_name='meetings')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='meetings')
    day_of_week = models.TextField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='upcoming')
    call_url = models.URLField(blank=True, null=True)
    date = models.DateField(blank=True, null=True)



    def generate_call_url(self):
        if not self.call_url:
            room_name = f"meeting-{self.id}-{get_random_string(6)}"
            self.call_url = f"https://meet.jit.si/{room_name}"
            self.save()

    def __str__(self):
        return f"Meeting for {self.user} with {self.advisor.first_name} on {self.day_of_week} {self.start_time} to {self.end_time}"


class Feedback(models.Model):
    meeting = models.OneToOneField(Meetings, on_delete=models.CASCADE, primary_key=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

