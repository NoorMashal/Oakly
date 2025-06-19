from django.contrib import admin
from .models import Transaction, Profile, FinancialAdvisorProfile, Availability, Meetings

# Register your models here.
admin.site.register(Transaction)
admin.site.register(Profile)
admin.site.register(FinancialAdvisorProfile)
admin.site.register(Availability)
admin.site.register(Meetings)