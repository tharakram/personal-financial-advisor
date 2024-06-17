from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# Function to generate Bank Account statements
def generate_bank_statement(output_filename):
    c = canvas.Canvas(output_filename, pagesize=letter)
    width, height = letter

    c.setFont("Helvetica", 14)
    c.drawString(30, height - 40, "ABC Bank Statement")
    c.setFont("Helvetica", 10)
    c.drawString(30, height - 60, "123 James St, PO Box 4000")
    c.drawString(30, height - 75, "VICTORIA BC V8X 3X4")

    # Statement Info
    c.setFont("Helvetica", 12)
    c.drawString(400, height - 40, "Statement Period")
    c.setFont("Helvetica", 10)
    c.drawString(380, height - 60, "Withdrawals/Deposits")
    c.drawString(380, height - 75, "2024-01-31 to 2024-05-07")
    
    # Account Info
    c.setFont("Helvetica", 12)
    c.drawString(30, height - 110, "Account Number: XXX XXX 3210")
    c.setFont("Helvetica", 10)
    c.drawString(30, height - 130, "Account Name: John DOe")
    c.drawString(30, height - 145, "Account Type: CHEQUING")

    # Transactions Table
    data = [
        ["Date", "Description", "Withdrawals ($)", "Desposits ($)", "Balance ($)"],
        ["2024-01-01", "Previous Balance", "", "", "$15,000.00"],
        ["2024-01-15", "XYZ LLC ACH Desposit -paycheck", "", "$7,000.00", "$22,000.00"],
        ["2024-01-31", "XYZ LLC ACH Desposit - paycheck", "", "$7,000.00", "$29,000.00"],
        ["2024-02-01", "Star Bank LLC - Mortgage Payment", "$3,000.00", "", "$26,000.00"],
        ["2024-02-02", "Zelle pay transfer - David", "$1,500.00", "", "$24,500.00"],      
        ["2024-02-10", "AAA Auto Insurance Premium", "$150.00", "", "$24,350.00"],
        ["2024-02-15", "XYZ LLC ACH Desposit - paycheck", "", "$7,000.00", "$31,350.00"],
        ["2024-02-29", "XYZ LLC ACH Desposit - paycheck", "", "$7,000.00", "$38,350.00"],
        ["2024-03-01", "Star Bank LLC - Mortgage Payment", "$3,000.00", "", "$35,350.00"],
        ["2024-03-03", "Credit Card Auto Payment", "$5,018.47", "", "30,331.53"],
        ["2024-03-10", "AAA Auto Insurance Premium", "$150.00", "", "$30,181.53"],
        ["2024-03-15", "XYZ LLC ACH Desposit - paycheck", "", "$7,000.00","$37,181.53"],
        ["2024-03-31", "XYZ LLC ACH Desposit - paycheck", "", "$7,000.00","$44,181.53"],
        ["2024-04-01", "Star Bank LLC - Mortgage Payment", "$3,000.00", "", "$41,181.53"],
        ["2024-04-03", "Credit Card Auto Payment", "$3,000", "", "$38,181.53"],
        ["2024-04-10", "AAA Auto Insurance Premium", "$150.00", "", "$38,031.53"],
        ["2024-04-15", "XYZ LLC ACH Desposit - paycheck", "", "$7,000.00","$45,031.53"],
        ["2024-04-31", "XYZ LLC ACH Desposit - paycheck", "", "$7,000.00","$52,031.53"],
        ["2024-05-01",  "Star Bank LLC  - Mortgage Payment", "$3,000.00", "",  "$49,031.53"],
        ["2024-05-03", "Credit Card Auto Payment", "$6,390.80", "", "$42,640.73"],
        ["2024-05-10", "AAA Auto Insurance Premium", "", "$150.00","$42,490.73"],
        ["2024-05-15", "XYZ LLC ACH Desposit - paycheck", "", "$7,000.00","$49,490.73"],
        ["2024-05-15", "ACH Wire Transfer - Wilkins", "$11,500.00", "", "$37,990.73"],
        ["2024-05-31", "XYZ LLC ACH Desposit - paycheck", "", "$7,000.00","$44,990.03"]
    ]

    table = Table(data, colWidths=[100, 200, 100, 100, 100])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.gray),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ("GRID",(0,0),(-1,-1), 1, colors.black),
    ]))

    table.wrapOn(c, width, height)
    table.drawOn(c, 30, height - 700)

    # Closing
    c.setFont('Helvetica', size=10)
    c.drawString(30, 50, "Thank you for banking with us.")

    c.showPage()
    c.save()



generate_bank_statement("John_Doe_Checking_Statement.pdf")