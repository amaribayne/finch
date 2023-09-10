from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from app.models import db, Expense, Goal
from collections import defaultdict
from datetime import datetime, timedelta
from operator import attrgetter
import plotly.express as px
import plotly.graph_objs as go
import pandas as pd
import requests

# Blueprint instance for this set of routes
bp = Blueprint('routes', __name__)

# Sample list to hold expenses
expenses = []

# Mapping of month names to their numeric values
month_mapping = {
    'January': 1,
    'February': 2,
    'March': 3,
    'April': 4,
    'May': 5,
    'June': 6,
    'July': 7,
    'August': 8,
    'September': 9,
    'October': 10,
    'November': 11,
    'December': 12
}


# Theme for Plotly graphs
def apply_custom_theme(fig):
    fig.update_layout(
        margin=dict(l=30, r=30, t=30, b=30),
        title="Month/Amount",
        paper_bgcolor="#1e1d1f",
        plot_bgcolor="#1e1d1f",
        xaxis_title_font=dict(color='white'),
        yaxis_title_font=dict(color='white'),
        title_font=dict(color='white'),
        xaxis_color="#ffffff",
        yaxis_color="#ffffff",
        xaxis=dict(gridcolor='grey'),
        yaxis=dict(gridcolor='grey')
    ).update_traces(
        line=dict(color='yellow')
    )


# Database creation
@bp.before_app_request
def create_tables():
    db.create_all()

# Home page
@bp.route('/')
def home():
    return render_template('home.html')

# Expenses page
@bp.route('/expenses')
def expenses():
    # Retrieve all expenses from the database
    expenses = Expense.query.all()
    
    # Create a dictionary to group expenses by month
    grouped_expenses = defaultdict(list)
    for expense in expenses:
        grouped_expenses[expense.month].append(expense)
    
    # Get a list of months sorted by their numeric values
    sorted_months = sorted(grouped_expenses.keys(), key=lambda month: month_mapping[month])

    # Calculate total amount spent per month
    total_amount_per_month = {}
    for month, expenses_list in grouped_expenses.items():
        total_amount = sum(expense.amount for expense in expenses_list)
        total_amount_per_month[month] = total_amount

    # Extract the data for the line plot
    line_data = []
    for month in sorted_months:
        expenses_for_month = grouped_expenses[month]
        total_amount = sum(expense.amount for expense in expenses_for_month)
        line_data.append({"Month": month, "Total Amount": total_amount})

    # Create a DataFrame from the line data
    line_df = pd.DataFrame(line_data)

    # Create Plotly graph
    fig = px.line(
        line_df,
        x="Month",
        y="Total Amount",
        labels={"Total Amount": "Total Amount Spent"},
        line_shape='linear',
        render_mode='svg'
    )

    # Sort months for graph
    fig.update_layout(
        xaxis_categoryorder='array',
        xaxis_categoryarray=sorted_months
    )

    apply_custom_theme(fig)

    graph_html = fig.to_html()
    
    return render_template('expenses.html', expenses=expenses,
    grouped_expenses=grouped_expenses, sorted_months=sorted_months,
    month_mapping=month_mapping, graph_html=graph_html, 
    total_amount_per_month=total_amount_per_month)

# Function to group expenses by month
def grouped_expenses(expenses):
    grouped = defaultdict(list)
    for expense in expenses:
        grouped[expense.month].append(expense)
    return grouped

# Route to add an expense
@bp.route('/add_expense', methods=['POST'])
def add_expense():
    # Get expense details from the form
    expense_description = request.form.get('description')
    expense_amount = float(request.form.get('amount'))
    expense_month = request.form.get('month')

    # Add the expense to the database and group it by month
    new_expense = Expense(description=expense_description, amount=expense_amount, month=expense_month)
    db.session.add(new_expense)
    db.session.commit()

    return redirect(url_for('routes.expenses'))

# Route to delete an expense
@bp.route('/delete_expense/<int:expense_index>', methods=['POST'])
def delete_expense(expense_index):
    # Find and delete the selected expense from the database
    expense_to_delete = Expense.query.get_or_404(expense_index)
    db.session.delete(expense_to_delete)
    db.session.commit()

    return redirect(url_for('routes.expenses'))

# Route to edit an expense
@bp.route('/edit_expense/<int:expense_index>', methods=['GET', 'POST'])
def edit_expense(expense_index):
    # Find the selected expense from the database
    expense = Expense.query.get_or_404(expense_index)

    if request.method == 'POST':
        # Get updated expense details from the form
        expense_description = request.form.get('description')
        expense_amount = float(request.form.get('amount'))
        expense_month = request.form.get('month')

        # Update the expense in the database
        expense.description = expense_description
        expense.amount = expense_amount
        expense.month = expense_month
        db.session.commit()

        return redirect(url_for('routes.expenses'))


    return render_template('edit.html', expense=expense, month_mapping=month_mapping)

# Investments page
@bp.route('/investments', methods=['GET', 'POST'])
def investments():
    if request.method == 'POST':
        ticker = request.form.get('ticker').upper()
        api_key = 'BLSRTONQY99SBHG6'

        # Fetch stock data
        url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={ticker}&apikey={api_key}'
        response = requests.get(url)
        data = response.json()

        if 'Time Series (Daily)' in data:
            time_series = data['Time Series (Daily)']
            dates = list(time_series.keys())
            prices = [float(entry['4. close']) for entry in time_series.values()]
            
            trace = go.Scatter(x=dates, y=prices, mode='lines', name='Stock Price')
            fig = go.Figure(data=[trace])
            apply_custom_theme(fig)
            graph_html = fig.to_html(full_html=False, default_height=500, default_width=700)

            return render_template('investments.html', ticker=ticker, graph_html=graph_html, dates=dates, prices=prices)

        else:
            error = "Stock data not available for the provided ticker."
            return render_template('investments.html', error=error)
            
    return render_template('investments.html', ticker=None)

# Goals page
@bp.route('/goals', methods=['GET', 'POST'])
def goals():
    if request.method == 'POST':
        income = float(request.form.get('income'))
        goal_price = float(request.form.get('goal_price'))
        description = request.form.get('description')
        
        if income and goal_price:
            goal = Goal(income=income, goal_price=goal_price, description=description)
            db.session.add(goal)
            db.session.commit()

    goals = Goal.query.all()
    
    for goal in goals:
        # Calculate the time it would take to reach the goal
        time_to_reach_goal = timedelta(days=goal.goal_price / goal.income)

        # Add the calculated time to the goal object
        goal.time_to_reach_goal = time_to_reach_goal

    return render_template('goals.html', goals=goals)


