from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from datetime import datetime
import pandas as pd
import os  # Added for file handling


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///expenses.db'
app.config['SECRET_KEY'] = 'your_secret_key'

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# Flask-Login setup
login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id)) if user_id.isdigit() else None

# Models
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    expenses = db.relationship('Expense', backref='user', lazy=True)
    budgets = db.relationship('Budget', backref='user', lazy=True)
    recurring_expenses = db.relationship('RecurringExpense', backref='user', lazy=True)

class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(100), nullable=False)
    date = db.Column(db.String(100), nullable=False)
    month = db.Column(db.String(7), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class Budget(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class RecurringExpense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(100), nullable=False)
    frequency = db.Column(db.String(50), nullable=False)
    next_due_date = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

@app.route('/')
@login_required
def home():
    # Always use the current month
    current_month = datetime.now().strftime('%Y-%m')

    # Fetch expenses for the current month
    expenses = Expense.query.filter_by(user_id=current_user.id, month=current_month).all()
    budget = Budget.query.filter_by(user_id=current_user.id).first()
    total_spent = sum(expense.amount for expense in expenses)

    # Prepare data for analytics
    categories = {}
    for expense in expenses:
        categories[expense.category] = categories.get(expense.category, 0) + expense.amount

    return render_template('index.html', expenses=expenses, total_spent=total_spent, budget=budget, alert=None, categories=categories)

@app.route('/add_expense', methods=['GET', 'POST'])
@login_required
def add_expense():
    if request.method == 'POST':
        amount = float(request.form['amount'])
        category = request.form['category']
        date = request.form['date']  # Get the date from the form input
        month = datetime.strptime(date, '%Y-%m-%d').strftime('%Y-%m')  # Extract the month from the date

        # Create a new expense
        new_expense = Expense(
            amount=amount,
            category=category,
            date=date,
            month=month,
            user_id=current_user.id
        )

        # Add the expense to the database
        db.session.add(new_expense)
        db.session.commit()

        # Flash a success message
        flash('Expense added successfully!', 'success')

        # Stay on the same page (add_expense.html)
        return render_template('add_expense.html')

    # If it's a GET request, just render the add_expense template
    return render_template('add_expense.html')

@app.route('/export_monthly_spending')
@login_required
def export_monthly_spending():
    selected_month = request.args.get('month', datetime.now().strftime('%Y-%m'))
    expenses = Expense.query.filter_by(user_id=current_user.id, month=selected_month).all()

    data = [{'Category': e.category, 'Amount': e.amount} for e in expenses]
    df = pd.DataFrame(data)

    file_path = f'monthly_spending_{selected_month}.csv'
    df.to_csv(file_path, index=False)

    return send_file(file_path, as_attachment=True)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            flash('Logged in successfully!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Login failed. Check your username and password.', 'danger')

    return render_template('login.html')

@app.route('/set_budget', methods=['GET', 'POST'])
@login_required
def set_budget():
    if request.method == 'POST':
        amount = float(request.form['amount'])
        budget = Budget.query.filter_by(user_id=current_user.id).first()
        
        if budget:
            budget.amount = amount
        else:
            budget = Budget(amount=amount, user_id=current_user.id)
            db.session.add(budget)
        
        db.session.commit()
        flash('Budget set successfully!', 'success')
        return redirect(url_for('home'))

    return render_template('set_budget.html')

@app.route('/recurring', methods=['GET', 'POST'])
@login_required
def recurring():
    if request.method == 'POST':
        amount = float(request.form['amount'])
        category = request.form['category']
        frequency = request.form['frequency']
        next_due_date = request.form['next_due_date']

        new_recurring = RecurringExpense(
            amount=amount,
            category=category,
            frequency=frequency,
            next_due_date=next_due_date,
            user_id=current_user.id
        )

        db.session.add(new_recurring)
        db.session.commit()

        flash('Recurring expense added successfully!', 'success')
        return redirect(url_for('recurring'))

    recurring_expenses = RecurringExpense.query.filter_by(user_id=current_user.id).all()
    return render_template('recurring.html', recurring_expenses=recurring_expenses)

@app.route('/monthly_spending', methods=['GET'])
@login_required
def monthly_spending():
    selected_month = request.args.get('month', datetime.now().strftime('%Y-%m'))
    
    # Fetch expenses for the selected month
    expenses = Expense.query.filter_by(user_id=current_user.id, month=selected_month).all()

    # Group expenses by category
    monthly_data = {}
    for expense in expenses:
        category = expense.category
        amount = expense.amount
        monthly_data[category] = monthly_data.get(category, 0) + amount

    return render_template('monthly_spending.html', monthly_data=monthly_data, selected_month=selected_month)

@app.route('/yearly_spending')
@login_required
def yearly_spending():
    # Fetch all expenses for the current user
    expenses = Expense.query.filter_by(user_id=current_user.id).all()

    # Group expenses by year and category
    yearly_data = {}
    for expense in expenses:
        year = expense.month[:4]  # Extract year from 'YYYY-MM'
        category = expense.category
        amount = float(expense.amount)  # Ensure amount is treated as a float

        if year not in yearly_data:
            yearly_data[year] = {}
        if category not in yearly_data[year]:
            yearly_data[year][category] = 0
        yearly_data[year][category] += amount

    return render_template('yearly_spending.html', yearly_data=yearly_data)

@app.route('/export')
@login_required
def export():
    expenses = Expense.query.filter_by(user_id=current_user.id).all()

    data = [{'Amount': e.amount, 'Category': e.category, 'Date': e.date} for e in expenses]
    df = pd.DataFrame(data)

    file_path = 'expenses.xlsx'
    df.to_excel(file_path, index=False)

    return send_file(file_path, as_attachment=True)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')

        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()

        flash('Account created successfully! Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))





if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
