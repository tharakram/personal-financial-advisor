import random
import locale
from datetime import datetime, timedelta
from faker import Faker
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

fake = Faker()

locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

def generate_random_transactions(statement_date, num_transactions: int):
    categories = ['Groceries', 'Restaurants', 'Gas', 'Utilities', 'Entertainment', 'Travel', 'Electronics', 'Clothing']
    transactions = []
    total = 0
    for _ in range(num_transactions):
        date = statement_date - timedelta(days=random.randint(1, 30))
        description = fake.company()
        category = random.choice(categories)
        amount = round(random.uniform(10.0, 500.0), 2)
        transactions.append((date, description, category, amount))
        total += amount

    purchases = locale.currency(total, grouping=True)
    print(f"Total Amount: {purchases}")

    transactions.sort(key=lambda x: x[0])
    return transactions, purchases


def currency_to_float(amount):
    return float(amount.replace('$', '').replace(',',''))


def float_to_currency(amount):
    return locale.currency(amount, grouping=True)

def generate_statement(user_name, account_number, statement_date, transactions, purchases):
    file_name = f"{user_name.replace(' ', '_')}_statement_{statement_date.strftime('%Y-%m')}_a.pdf"
    c = canvas.Canvas(file_name, pagesize=letter)
    width, height = letter

    # Summary Amounts
    prev_balance = 6390.80
    payment = 6390.80
    remaining_balance = prev_balance - payment
    interest = 0.00
    fee = 0.00

    # Title and account information
    c.setFont("Helvetica-Bold", 16)
    c.drawString(1 * inch, height - 1 * inch, f"{user_name} Statement")

    c.setFont("Helvetica", 12)
    c.drawString(1 * inch, height - 1.5 * inch, f"Account: {account_number}")
    c.drawString(1 * inch, height - 1.75 * inch, f"Statement Date: {statement_date.strftime('%B %Y')}")
    c.drawString(1 * inch, height - 2 * inch, f"Payment Due Date: {(statement_date + timedelta(days=25)).strftime('%B %d, %Y')}")

    # Summary of Account
    c.setFont("Helvetica-Bold", 14)
    c.drawString(1 * inch, height - 2.5 * inch, "Summary of Account")
    c.setFont("Helvetica", 12)
    c.drawString(1 * inch, height - 2.75 * inch, "Previous Balance:")
    c.drawString(4 * inch, height - 2.75 * inch, f"{float_to_currency(prev_balance)}")
    c.drawString(1 * inch, height - 3 * inch, "Payments:")
    c.drawString(4 * inch, height - 3 * inch, f"{float_to_currency(payment)}")
    c.drawString(1 * inch, height - 3.25 * inch, "Purchases:")
    c.drawString(4 * inch, height - 3.25 * inch, f"{purchases}")
    c.drawString(1 * inch, height - 3.5 * inch, "Fees:")
    c.drawString(4 * inch, height - 3.5 * inch, f"{float_to_currency(fee)}")
    c.drawString(1 * inch, height - 3.75 * inch, "Interest Charged:")
    c.drawString(4 * inch, height - 3.75 * inch, f"{float_to_currency(interest)}")
    total = remaining_balance + interest + currency_to_float(purchases)
    
    c.drawString(1 * inch, height - 4 * inch, "Current Balance:")
    c.drawString(4 * inch, height - 4 * inch, f"{float_to_currency(total)}")

    # Transaction Details
    c.setFont("Helvetica-Bold", 14)
    c.drawString(1 * inch, height - 4.5 * inch, "Transaction Details")

    # Table Headers
    c.setFont("Helvetica-Bold", 12)
    c.drawString(1 * inch, height - 5 * inch, "Date")
    c.drawString(2 * inch, height - 5 * inch, "Description")
    c.drawString(5 * inch, height - 5 * inch, "Category")
    c.drawString(6.5 * inch, height - 5 * inch, "Amount ($)")

    # Transactions
    y = height - 5.25 * inch
    c.setFont("Helvetica", 12)

    # Remaining balance
    c.drawString(1 * inch, y, statement_date.strftime("%Y-%m-%d"))
    c.drawString(2 * inch, y, "Remaining Balance")
    c.drawString(5 * inch, y, "")
    c.drawString(6.5 * inch, y, f"{float_to_currency(remaining_balance)}")
    y -= 0.25 * inch

    for date, description, category, amount in transactions:
        c.drawString(1 * inch, y, date.strftime("%Y-%m-%d"))
        c.drawString(2 * inch, y, description)
        c.drawString(5 * inch, y, category)
        c.drawString(6.5 * inch, y, f"{amount:.2f}")
        y -= 0.25 * inch
        if y < 1 * inch:
            c.showPage()
            y = height - 1 * inch
            
    # Total
    c.setFont("Helvetica-Bold", 14)
    c.drawString(3 * inch, height - 7.5 * inch, "Total")
    c.drawString(6 * inch, height - 7.5 * inch, f"{float_to_currency(total)}")

    # Footer with Payment Slip
    c.setFont("Helvetica-Bold", 14)
    c.drawString(1 * inch, 1 * inch, "Payment Slip")
    c.setFont("Helvetica", 12)
    c.drawString(1 * inch, 0.75  * inch, f"Account Number: {account_number}")
    c.drawString(1 * inch, 0.5 * inch, f"Total Due: {float_to_currency(total)}")
    c.drawString(3 * inch, 0.25 * inch, f"Due Date: {(statement_date + timedelta(days=25)).strftime('%B %d, %Y')}")

    # Save
    c.save()
    print(f"Statement saved as {file_name}")


user_name = "John Doe"
account_number = "9876 XXXX XXXX 3210"
statement_date = "2024-05-07"
statement_date = datetime.strptime(statement_date, "%Y-%m-%d")
print(statement_date)
transactions, purchases = generate_random_transactions(statement_date, 20)
generate_statement(user_name, account_number, statement_date, transactions, purchases)