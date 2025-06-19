import csv
import json
import os
from datetime import date, datetime, timedelta
from io import TextIOWrapper
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User, Group
from django.db.models import Sum
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.http import JsonResponse
from .forms import LoginForm, UploadFileForm, SignupForm, TransactionForm, AvailabilityFormSet
from .models import Transaction, Profile, FinancialAdvisorProfile, Availability, Meetings
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.utils import timezone
from django.db.models import Q
from .forms import FeedbackForm
from django.contrib import messages
from google import genai
from django.contrib.auth.views import PasswordResetView
from django.contrib.auth.models import User
from django.urls import reverse_lazy



def calculate_recommended_budget(user):
    from datetime import date
    from Oakley.models import Transaction, Profile
    from django.db.models import Sum

    today = date.today()
    remaining_months = 12 - today.month + 1  # include current month

    try:
        profile = Profile.objects.get(user=user)
        goal = profile.savings_goal
        monthly_income = profile.monthly_income
    except Profile.DoesNotExist:
        return None  # or default recommendation

    # Total saved so far this year
    jan_1 = date(today.year, 1, 1)
    income = Transaction.objects.filter(user=user, date__gte=jan_1, transaction_type='income').aggregate(Sum('amount'))['amount__sum'] or 0
    expenses = Transaction.objects.filter(user=user, date__gte=jan_1, transaction_type='expense').aggregate(Sum('amount'))['amount__sum'] or 0
    current_savings = income - expenses

    remaining_needed = max(goal - current_savings, 0)
    monthly_savings_target = remaining_needed / remaining_months
    recommended_spending = monthly_income - monthly_savings_target

    return round(recommended_spending, 2)


def get_dashboard_context(user):
    from datetime import date, timedelta
    from Oakley.models import Transaction, Profile
    from django.db.models import Sum
    import json

    total_spending = Transaction.objects.filter(user=user, transaction_type='expense').aggregate(total=Sum('amount'))['total'] or 0

    try:
        user_profile = Profile.objects.get(user=user)
        total_income = user_profile.monthly_income
        budget_limit = total_income * 0.8
    except Profile.DoesNotExist:
        total_income = 5543.72
        budget_limit = 4000.00

    total_balance = total_income - total_spending

    today = date.today()
    first_day_of_month = date(today.year, today.month, 1)
    first_day_next_month = (first_day_of_month.replace(day=28) + timedelta(days=4)).replace(day=1)

    current_month_income = Transaction.objects.filter(
        user=user,
        date__gte=first_day_of_month,
        date__lt=first_day_next_month,
        transaction_type='income'
    ).aggregate(total=Sum('amount'))['total'] or 0

    current_month_expense = Transaction.objects.filter(
        user=user,
        date__gte=first_day_of_month,
        date__lt=first_day_next_month,
        transaction_type='expense'
    ).aggregate(total=Sum('amount'))['total'] or 0

    budget_percentage = min(round((total_spending / budget_limit) * 100 if budget_limit else 0), 100)

    recent_transactions = Transaction.objects.filter(user=user).order_by('-date')[:5]

    monthly_data = Transaction.objects.filter(user=user).order_by("date")
    chart_data = {
        "labels": [t.date.strftime("%b %d") for t in monthly_data],
        "income": [abs(t.amount) if t.transaction_type == 'income' else 0 for t in monthly_data],
        "expenses": [abs(t.amount) if t.transaction_type == 'expense' else 0 for t in monthly_data],
    }

    category_spending = Transaction.objects.filter(
        user=user,
        transaction_type='expense'
    ).values('category').annotate(
        total=Sum('amount')
    ).order_by('-total')

    category_data = {
        'labels': [item['category'] for item in category_spending],
        'values': [abs(float(item['total'])) for item in category_spending]
    }

    payment_methods = Transaction.objects.filter(
        user=user,
        transaction_type='expense'
    ).values('payment_method').annotate(
        total=Sum('amount')
    ).order_by('-total')

    payment_method_data = {
        'labels': [item['payment_method'] for item in payment_methods],
        'values': [abs(float(item['total'])) for item in payment_methods]
    }

    current_year = 2024
    months_data = []
    monthly_expenses = []
    monthly_income_data = []

    for month in range(1, 13):
        start_date = date(current_year, month, 1)
        end_date = (start_date.replace(day=28) + timedelta(days=4)).replace(day=1)

        month_name = start_date.strftime("%b")
        months_data.append(month_name)

        month_expense = Transaction.objects.filter(
            user=user,
            date__gte=start_date,
            date__lt=end_date,
            transaction_type='expense'
        ).aggregate(total=Sum('amount'))['total'] or 0

        monthly_expenses.append(abs(float(month_expense)))

        month_income = Transaction.objects.filter(
            user=user,
            date__gte=start_date,
            date__lt=end_date,
            transaction_type='income'
        ).aggregate(total=Sum('amount'))['total'] or 0

        monthly_income_data.append(abs(float(month_income)))
    recommended_budget = calculate_recommended_budget(user)

    return {
        "user": user,
        "total_spending": total_spending,
        "total_income": total_income,
        "total_balance": total_balance,
        "budget_limit": budget_limit,
        "budget_percentage": budget_percentage,
        "recent_transactions": recent_transactions,
        "chart_data": json.dumps(chart_data),
        "category_data": json.dumps(category_data),
        "payment_method_data": json.dumps(payment_method_data),
        "monthly_comparison": json.dumps({
            "months": months_data,
            "expenses": monthly_expenses,
            "income": monthly_income_data
        }),
        "monthly_income_chart": json.dumps({
            "months": months_data,
            "income": monthly_income_data
        }),
        "monthly_expense_chart": json.dumps({
            "months": months_data,
            "expenses": monthly_expenses
        }),
        "current_month_income": abs(float(current_month_income)),
        "current_month_expense": abs(float(current_month_expense)),
        "recommended_budget": recommended_budget,
    }

@login_required(login_url='Oakley:login')
def home(request):
    user = request.user

    try:
        profile1 = Profile.objects.get(user=user)
    except Profile.DoesNotExist:
        profile1 = None

    if profile1 is None:
        return redirect(reverse('Oakley:questionnaire'))

    context = get_dashboard_context(user)
    context['recommended_budget'] = calculate_recommended_budget(user)
    context['open_modal'] = False
    context['response'] = ""

    if request.method == "POST":
        context['open_modal'] = True
        gemini_api_key = os.getenv('GEMINI_API_KEY')
        client = genai.Client(api_key=gemini_api_key)
        profile1 = Profile.objects.get(user=user)
        transaction1 = Transaction.objects.filter(user=user)
        question = (f"Summarize my spending habits based on the following transactions. " +
                    f"Highlight any significant spending categories or patterns. " +
                    f"Keep the feedback to a maximum of three to four short sentences.\n" +
                    f"Profile Information: {str(profile1)}\n" +
                    f"Transactions: {str(transaction1)}\n")

        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[question],
        )
        context['response'] = response.text
        return render(request, "Oakley/home.html", context)

    return render(request, "Oakley/home.html", context)


@login_required(login_url='Oakley:login')
def transactions(request):
    user = request.user
    sort_by = request.GET.get('sort', 'date')  # default sort by date
    direction = request.GET.get('dir', 'asc')

    if direction == 'desc':
        sort_by = f'-{sort_by}'

    transactions_list = Transaction.objects.filter(user=user).order_by(sort_by).values_list(
        'id', 'date', 'category', 'merchant', 'amount', 'payment_method', 'location'
    )

    return render(request, 'Oakley/transactions.html', {
        'items': transactions_list,
        'current_sort': sort_by.strip('-'),
        'current_dir': direction,
    })

@login_required(login_url='Oakley:login')
def import_transactions(request):
    if request.method == "POST":
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            with TextIOWrapper(request.FILES['file'], encoding='utf-8') as file:
                reader = csv.DictReader(file)
                user = request.user

                income_keywords = ['income', 'deposit', 'payroll', 'transfer in']

                for row in reader:
                    try:
                        t_date = row['Date']
                        category = row['Category']
                        merchant = row['Merchant']
                        amount = row['Amount']
                        method = row['Payment Method']
                        location = row['Location']

                        # Parse and clean data
                        date_obj = datetime.strptime(t_date, "%Y-%m-%d").date()
                        amount_value = float(amount) if amount else 0.0
                        category_lower = category.strip().lower()

                        transaction_type = 'income' if amount_value > 0 else 'expense'

                        Transaction.objects.create(
                            user=user,
                            date=date_obj,
                            category=category.strip(),
                            merchant=merchant.strip(),
                            amount=amount_value,
                            payment_method=method.strip(),
                            location=location.strip(),
                            transaction_type=transaction_type
                        )
                    except Exception as e:
                        print(f"Skipping row due to error: {e}")
                        continue

                return redirect(reverse('Oakley:transactions'))
    return render(request, 'Oakley/transactions.html')



@csrf_exempt
@login_required(login_url='Oakley:login')
@login_required(login_url='Oakley:login')
def edit_transaction(request, transaction_id):
    transaction = get_object_or_404(Transaction, id=transaction_id, user=request.user)

    if request.method == "POST":
        try:
            data = json.loads(request.body)

            # Debugging: Print incoming data
            print("Received Data:", data)

            # Update transaction fields
            transaction.date = data.get("date", transaction.date)
            transaction.category = data.get("category", transaction.category)
            transaction.merchant = data.get("merchant", transaction.merchant)
            transaction.amount = float(data.get("amount", transaction.amount))
            transaction.payment_method = data.get("payment_method", transaction.payment_method)
            transaction.location = data.get("location", transaction.location)
            transaction.save()

            return JsonResponse({"success": True})  # Return success response
        except json.JSONDecodeError:
            return JsonResponse({"success": False, "error": "Invalid JSON"}, status=400)
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=400)

    return JsonResponse({"success": False, "error": "Invalid request"}, status=400)


@login_required(login_url='Oakley:login')
def delete_transaction(request, transaction_id):
    transaction = get_object_or_404(Transaction, id=transaction_id, user=request.user)

    if request.method == "POST":
        transaction.delete()
        return JsonResponse({"success": True})  # Return JSON response for AJAX

    return JsonResponse({"success": False}, status=400)  # Handle errors


def signup_view(request):
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect(reverse('Oakley:questionnaire'))
    else:
        form = SignupForm()
    return render(request, 'Oakley/signup.html', {'form': form})


def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                if user.groups.filter(name="Financial Advisor").exists():
                    advisor_profile1 = FinancialAdvisorProfile.objects.get(user=user)
                    if advisor_profile1.firm_name is None:
                        return redirect(reverse('Oakley:advisor_questionnaire'))
                    return redirect(reverse('Oakley:advisor_home'))

                try:
                    profile1 = Profile.objects.get(user=user)
                except Profile.DoesNotExist:
                    profile1 = None

                if profile1 is None:
                    return redirect(reverse('Oakley:questionnaire'))
                return redirect(reverse('Oakley:home'))
            else:
                form.add_error(None, "Invalid username or password.")

    else:
        form = LoginForm()

    return render(request, 'Oakley/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect(reverse('Oakley:login'))


@login_required(login_url='Oakley:login')
def budget_planning(request):
    user = request.user
    try:
        profile = Profile.objects.get(user=user)
    except Profile.DoesNotExist:
        return redirect('Oakley:questionnaire')

    recommended_budget = calculate_recommended_budget(user)

    # Simple assumptions (can be improved later with category tagging logic)
    estimated_fixed = recommended_budget * 0.5 if recommended_budget else 0
    estimated_variable = recommended_budget * 0.3 if recommended_budget else 0
    safe_to_spend = recommended_budget - (estimated_fixed + estimated_variable) if recommended_budget else None

    return render(request, "Oakley/budget_planning.html", {
        "recommended_budget": recommended_budget,
        "estimated_fixed": round(estimated_fixed, 2),
        "estimated_variable": round(estimated_variable, 2),
        "safe_to_spend": round(safe_to_spend, 2) if safe_to_spend is not None else None,
    })




def reports(request):
    return render(request, "Oakley/reports.html")


@login_required(login_url='Oakley:login')
def questionnaire(request):
    user = request.user
    if request.method == "POST":
        monthly_income = request.POST.get("monthly_income")
        income_stability = request.POST.get("income_stability")
        recurring_bills = request.POST.getlist("recurring_bills")
        variable_spending = request.POST.getlist("variable_spending")
        primary_goal = request.POST.get("primary_goal")
        savings_goal = request.POST.get("savings_goal")
        expense_tracking = request.POST.get("expense_tracking")

        try:
            profile1 = Profile.objects.get(user=user)
        except Profile.DoesNotExist:
            profile1 = None

        if profile1 is None:
            profile2 = Profile.objects.create(
                user=user,
                monthly_income=float(monthly_income),
                income_stability=income_stability,
                recurring_bills=', '.join(recurring_bills),
                variable_spending=', '.join(variable_spending),
                primary_goal=primary_goal,
                savings_goal=float(savings_goal),
                expense_tracking=expense_tracking,
            )
            profile2.save()
            return redirect(reverse('Oakley:home'))
        else:
            Profile.objects.filter(user=user).update(
                user=user,
                monthly_income=float(monthly_income),
                income_stability=income_stability,
                recurring_bills=', '.join(recurring_bills),
                variable_spending=', '.join(variable_spending),
                primary_goal=primary_goal,
                savings_goal=float(savings_goal),
                expense_tracking=expense_tracking,
            )
            return redirect(reverse('Oakley:profile'))

    return render(request, "Oakley/questionnaire.html")


@login_required(login_url='Oakley:login')
def profile(request):
    user = request.user
    try:
        profile1 = Profile.objects.get(user=user)
    except Profile.DoesNotExist:
        profile1 = None

    if profile1 is None:
        return redirect(reverse('Oakley:questionnaire'))

    return render(request, "Oakley/profile.html", {'profile': profile1})


@login_required(login_url='Oakley:login')
def add_transaction(request):
    if request.method == "POST":
        form = TransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.user = request.user
            transaction.save()
        # Either way, redirect to the transactions page
        return redirect('Oakley:transactions')
    # If someone tries to access it via GET, redirect them
    return redirect('Oakley:transactions')



def advisor_signup(request):
    if request.method == "POST":
        first_name = request.POST.get("firstName")
        last_name = request.POST.get("lastName")
        phone_number = request.POST.get("phoneNumber")
        email = request.POST.get("email")
        username = request.POST.get("username")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirmPassword")

        if User.objects.filter(username=username).exists():
            return render(request, 'Oakley/advisor/signup.html', {'error': 'Username already exists'})
        else:
            if len(password) < 8:
                return render(request, 'Oakley/advisor/signup.html',
                              {'error': 'password must be at least 8 characters'})
            if password != confirm_password:
                return render(request, 'Oakley/advisor/signup.html', {'error': 'passwords do not match'})

            user = User.objects.create_user(username=username, password=password, email=email)
            user.save()

            user.backend = 'django.contrib.auth.backends.ModelBackend'  # Ensure correct backend

            group, _ = Group.objects.get_or_create(name="Financial Advisor")
            user.groups.add(group)

            login(request, user)

            financial_advisor_profile = FinancialAdvisorProfile.objects.create(
                user=user,
                first_name=first_name,
                last_name=last_name,
                phone_number=phone_number,
            )
            financial_advisor_profile.save()

            return redirect(reverse('Oakley:advisor_questionnaire'))

    return render(request, 'Oakley/advisor/signup.html')


@login_required(login_url='Oakley:login')
def advisor_home(request):
    return render(request, 'Oakley/advisor/meetings.html')


@login_required(login_url='Oakley:login')
def advisor_profile(request):
    return render(request, 'Oakley/advisor/profile.html',
                  {'profile': FinancialAdvisorProfile.objects.get(user=request.user)})


@login_required(login_url='Oakley:login')
def advisor_questionnaire(request):
    user = request.user
    advisor_profile = FinancialAdvisorProfile.objects.get(user=user)

    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

    if request.method == "POST":
        # Update advisor info
        firm_name = request.POST.get("firm_name")
        certifications = request.POST.get("certifications")
        experience_years = request.POST.get("experience")
        bio = request.POST.get("bio")
        specialties = request.POST.get("specialties")
        website = request.POST.get("website")
        linkedin = request.POST.get("linkedin")
        location = request.POST.get("location")

        FinancialAdvisorProfile.objects.filter(user=user).update(
            firm_name=firm_name,
            certifications=certifications,
            experience_years=experience_years,
            bio=bio,
            specialties=specialties,
            website=website,
            linkedin=linkedin,
            location=location,
        )

        # ✅ Save new availability entries
        Availability.objects.filter(advisor=advisor_profile).delete()

        for day in days:
            if request.POST.get(f'{day}_available'):
                start = request.POST.get(f'{day}_start')
                end = request.POST.get(f'{day}_end')
                if start and end:
                    available = Availability.objects.create(
                        advisor=advisor_profile,
                        day_of_week=day,
                        start_time=start,
                        end_time=end
                    )
                    available.save()

        return redirect(reverse('Oakley:advisor_home'))

    return render(request, 'Oakley/advisor/questionnaire.html', {
        'advisor': advisor_profile,
        'days': days
    })


@login_required(login_url='Oakley:login')
def meetings(request):
    context = {}
    user_meetings = Meetings.objects.filter(user=request.user, status='upcoming')

    prev_meetings = Meetings.objects.filter(
        Q(status='completed') | Q(status='canceled'),
        user=request.user
    )
    context['meetings'] = user_meetings
    context['prev_meetings'] = prev_meetings
    return render(request, 'Oakley/meetings.html', context)


#Make sure that only the user can join the meeting id url
@login_required(login_url='Oakley:login')
def join_meetings(request, meeting_id):
    meeting = get_object_or_404(Meetings, pk=meeting_id)
    return render(request, 'Oakley/join_meetings.html', {'meeting': meeting})


#make sure only the user who owns the meeting can cancel
@login_required(login_url='Oakley:login')
def cancel_meeting(request, meeting_id):
    meeting = get_object_or_404(Meetings, id=meeting_id)

    if request.method == 'POST' and meeting.status == 'upcoming':
        meeting.status = 'canceled'
        meeting.save()

    # Redirect back to the page that made the request
    return redirect(request.META.get('HTTP_REFERER', 'Oakley:landing'))

#make sure only the user who owns the meeting can mark complete
@login_required(login_url='Oakley:login')
def complete_meeting(request, meeting_id):
    meeting = get_object_or_404(Meetings, id=meeting_id)

    if request.method == 'POST' and meeting.status == 'upcoming':
        meeting.status = 'completed'
        meeting.save()

    # Redirect back to the page that made the request
    return redirect(reverse('Oakley:advisor_meetings'))

@login_required(login_url='Oakley:login')
def advisor_meetings(request):
    context = {}
    advisor = FinancialAdvisorProfile.objects.get(user=request.user)
    meetings = Meetings.objects.filter(advisor=advisor, status='upcoming')
    prev_meetings = Meetings.objects.filter(
        Q(status='completed') | Q(status='canceled'),
        advisor=advisor
    ).select_related('feedback')
    context['meetings'] = meetings
    context['prev_meetings'] = prev_meetings

    return render(request, 'Oakley/advisor/meetings.html', context)

@login_required(login_url='Oakley:login')
def give_feedback(request, meeting_id):
    meeting = get_object_or_404(Meetings, id=meeting_id, advisor__user=request.user, status__in=['completed', 'canceled'])

    # If feedback exists, load it; else create new
    feedback = getattr(meeting, 'feedback', None)

    if request.method == 'POST':
        form = FeedbackForm(request.POST, instance=feedback)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.meeting = meeting
            feedback.author = request.user
            feedback.save()
            messages.success(request, "Feedback submitted successfully.")
            return redirect('Oakley:advisor_meetings')
    else:
        form = FeedbackForm(instance=feedback)

    return render(request, 'Oakley/advisor/give_feedback.html', {
        'form': form,
        'meeting': meeting
    })

@login_required(login_url='Oakley:login')
def edit_feedback(request, meeting_id):
    meeting = get_object_or_404(Meetings, id=meeting_id, advisor__user=request.user)
    feedback = get_object_or_404(meeting.feedback.__class__, meeting=meeting)

    if request.method == 'POST':
        form = FeedbackForm(request.POST, instance=feedback)
        if form.is_valid():
            form.save()
            messages.success(request, "Feedback updated successfully.")
            return redirect('Oakley:advisor_meetings')
    else:
        form = FeedbackForm(instance=feedback)

    return render(request, 'Oakley/advisor/edit_feedback.html', {
        'form': form,
        'meeting': meeting
    })
@login_required(login_url='Oakley:login')
def schedule(request):
    user = request.user
    advisors = FinancialAdvisorProfile.objects.all()
    availability = Availability.objects.all()
    available_advisors = [a.advisor for a in Availability.objects.all()]
    advisor_not_available = [advisor for advisor in advisors if advisor not in available_advisors]

    day_map = {
        "monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3, "friday": 4, "saturday": 5, "sunday": 6
    }

    if request.method == "POST":
        advisor_username = request.POST.get("advisor_username")
        day, start_time, end_time = request.POST.get('time_choice').split(',')
        advisor_user = User.objects.get(username=advisor_username)
        advisor_profile1 = FinancialAdvisorProfile.objects.get(user=advisor_user)

        normalized_time_string1 = start_time.replace('.', '').lower()
        start_time_obj = datetime.strptime(normalized_time_string1, '%I:%M %p').time()
        normalized_time_string2 = end_time.replace('.', '').lower()
        end_time_obj = datetime.strptime(normalized_time_string2, '%I:%M %p').time()

        meetings = Meetings.objects.filter(advisor=advisor_profile1, status='upcoming')
        for meeting in meetings:
            if meeting.day_of_week == day and meeting.start_time == start_time_obj and meeting.end_time == end_time_obj:
                messages.error(request, "Meeting already scheduled for this time. Please choose another time.")
                return render(request, 'Oakley/schedule.html', {'advisors': advisors, 'availability': availability, 'advisor_not_available': advisor_not_available, 'show_toast': False})

        today = timezone.now().date()
        current_weekday = today.weekday()  # Monday=0, Sunday=6
        days_ahead = (day_map.get(day.lower()) - current_weekday + 7) % 7
        if days_ahead == 0:
            days_ahead = 7
        next_date = today + timedelta(days=days_ahead)

        meeting = Meetings.objects.create(
            advisor=advisor_profile1,
            user=user,
            day_of_week=day,
            date=next_date,
            start_time=start_time_obj,
            end_time=end_time_obj,
        )
        meeting.generate_call_url()
        meeting.save()
        return render(request, 'Oakley/schedule.html', {'advisors': advisors, 'availability': availability, 'available_advisors':available_advisors, 'advisor_not_available':advisor_not_available, 'show_toast': True})

    return render(request, 'Oakley/schedule.html', {'advisors': advisors, 'availability': availability, 'available_advisors':available_advisors, 'advisor_not_available':advisor_not_available, 'show_toast': False})

@login_required
def advisor_view_user_dashboard(request, user_id):
    advisor = FinancialAdvisorProfile.objects.get(user=request.user)
    user = get_object_or_404(User, id=user_id)

    # Check if this advisor has a scheduled meeting with this user
    has_meeting = Meetings.objects.filter(advisor=advisor, user=user).exists()
    if not has_meeting:
        raise PermissionDenied("You do not have permission to view this dashboard.")

    context = get_dashboard_context(user)
    return render(request, "Oakley/advisor/user_dashboard.html", context)

class OakleyPasswordResetView(PasswordResetView):
    template_name = 'Oakley/password_reset.html'
    email_template_name = 'Oakley/registration/password_reset_email.html'
    subject_template_name = 'registration/password_reset_subject.txt'
    success_url = reverse_lazy('Oakley:login')

    def get_email_options(self):
        return {
            'email_template_name': self.email_template_name,
            'subject_template_name': self.subject_template_name,
            'use_https': self.request.is_secure(),
            'from_email': self.from_email,
            'request': self.request,
            'html_email_template_name': self.html_email_template_name,
            'extra_email_context': {
                'domain': 'localhost:8000',
                'protocol': 'http',
                'site_name': 'Oakley',
            }
        }