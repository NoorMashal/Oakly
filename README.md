# Oakly – Personal Finance Web App

Oakly is a Django-based personal finance application designed to help users manage budgets, track expenses, and plan savings goals with ease. It offers features like recurring expense scheduling, monthly spending suggestions, and a clean, responsive interface.

![Oakly Screenshot](https://i.imgur.com/azTBZOp.png)

## Features

- Track income and expenses
- Schedule recurring costs (e.g., rent, subscriptions)
- Automatic calculation of spending limits based on savings goals
- User authentication and account management
- Clean UI with HTML/CSS
- PostgreSQL-powered backend for robust data handling

## Tech Stack

**Backend**: Python, Django  
**Database**: PostgreSQL  
**Frontend**: HTML, CSS  
**Other Tools**: Git, GitHub Projects (Agile workflow)

## Getting Started

Clone the repository, set up your environment, run migrations, and start the server:

```bash
git clone https://github.com/YourUsername/oakly.git
cd oakly
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
