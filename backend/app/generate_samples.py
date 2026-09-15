"""
Generate sample documents for testing the classifier.
Creates realistic-looking document images using Pillow + ReportLab.
"""

from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import random

SAMPLE_DIR = Path(__file__).parent / "sample_docs"
SAMPLE_DIR.mkdir(exist_ok=True)

# Document size
WIDTH, HEIGHT = 800, 1100
BG_COLOR = (255, 255, 255)
TEXT_COLOR = (30, 30, 30)
HEADER_COLOR = (20, 60, 120)
ACCENT_COLOR = (0, 120, 80)


def get_font(size=16):
    """Get a font, falling back to default if system fonts unavailable."""
    font_paths = [
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/SFPro.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for fp in font_paths:
        try:
            return ImageFont.truetype(fp, size)
        except (OSError, IOError):
            continue
    return ImageFont.load_default()


def draw_header(draw, title, subtitle=""):
    """Draw a document header."""
    draw.rectangle([(0, 0), (WIDTH, 120)], fill=HEADER_COLOR)
    draw.text((40, 30), title, fill=(255, 255, 255), font=get_font(28))
    if subtitle:
        draw.text((40, 70), subtitle, fill=(200, 220, 255), font=get_font(16))
    draw.line([(0, 120), (WIDTH, 120)], fill=ACCENT_COLOR, width=3)


def draw_field(draw, x, y, label, value, bold_value=False):
    """Draw a label-value pair."""
    draw.text((x, y), label, fill=(100, 100, 100), font=get_font(14))
    draw.text((x + 200, y), str(value), fill=TEXT_COLOR, font=get_font(16))
    draw.line([(x, y + 28), (x + WIDTH - 80, y + 28)], fill=(230, 230, 230), width=1)


def draw_table_header(draw, x, y, columns, widths):
    """Draw a table header row."""
    draw.rectangle([(x, y), (x + sum(widths), y + 35)], fill=(240, 245, 255))
    cx = x
    for col, w in zip(columns, widths):
        draw.text((cx + 10, y + 8), col, fill=HEADER_COLOR, font=get_font(13))
        cx += w
    draw.line([(x, y + 35), (x + sum(widths), y + 35)], fill=HEADER_COLOR, width=1)


def draw_table_row(draw, x, y, values, widths, highlight=False):
    """Draw a table data row."""
    bg = (255, 255, 255) if not highlight else (245, 255, 245)
    draw.rectangle([(x, y), (x + sum(widths), y + 30)], fill=bg)
    cx = x
    for val, w in zip(values, widths):
        draw.text((cx + 10, y + 6), str(val), fill=TEXT_COLOR, font=get_font(14))
        cx += w
    draw.line([(x, y + 30), (x + sum(widths), y + 30)], fill=(240, 240, 240), width=1)


# ─── Payslip ──────────────────────────────────────────────────────────────

def generate_payslip():
    img = Image.new("RGB", (WIDTH, HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(img)
    
    draw_header(draw, "EMPLOYEE PAYSLIP", "Pay Period: March 2026 | ABC Pty Ltd")
    
    y = 160
    draw_field(draw, 40, y, "Employee Name:", "John Smith"); y += 35
    draw_field(draw, 40, y, "Employee ID:", "EMP-2024-0847"); y += 35
    draw_field(draw, 40, y, "ABN:", "51 824 753 556"); y += 35
    draw_field(draw, 40, y, "Pay Date:", "15 March 2026"); y += 35
    draw_field(draw, 40, y, "Pay Frequency:", "Monthly"); y += 50
    
    # Earnings table
    draw.text((40, y), "EARNINGS", fill=HEADER_COLOR, font=get_font(18)); y += 35
    cols = ["Description", "Hours", "Rate", "Amount"]
    widths = [250, 120, 120, 150]
    draw_table_header(draw, 40, y, cols, widths); y += 36
    draw_table_row(draw, 40, y, ["Base Salary", "160", "$45.00", "$7,200.00"], widths); y += 31
    draw_table_row(draw, 40, y, ["Overtime", "8", "$67.50", "$540.00"], widths); y += 31
    draw_table_row(draw, 40, y, ["Allowance", "-", "-", "$300.00"], widths, highlight=True); y += 40
    
    gross = "$8,040.00"
    draw.text((400, y), "Gross Pay:", fill=TEXT_COLOR, font=get_font(16))
    draw.text((530, y), gross, fill=ACCENT_COLOR, font=get_font(18)); y += 45
    
    # Deductions
    draw.text((40, y), "DEDUCTIONS", fill=(180, 40, 40), font=get_font(18)); y += 35
    cols2 = ["Description", "", "", "Amount"]
    draw_table_header(draw, 40, y, cols2, widths); y += 36
    draw_table_row(draw, 40, y, ["Income Tax", "", "", "$1,892.00"], widths); y += 31
    draw_table_row(draw, 40, y, ["Superannuation", "", "", "$884.40"], widths); y += 31
    draw_table_row(draw, 40, y, ["Medicare Levy", "", "", "$160.80"], widths); y += 45
    
    # Net Pay
    draw.rectangle([(40, y), (WIDTH - 40, y + 50)], fill=(230, 245, 230))
    draw.text((60, y + 12), "NET PAY:", fill=HEADER_COLOR, font=get_font(20))
    draw.text((530, y + 12), "$5,102.80", fill=ACCENT_COLOR, font=get_font(22))
    
    img.save(SAMPLE_DIR / "sample_payslip.png")
    print("✅ Generated: sample_payslip.png")


# ─── Bank Statement ───────────────────────────────────────────────────────

def generate_bank_statement():
    img = Image.new("RGB", (WIDTH, HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(img)
    
    draw_header(draw, "COMMONWEALTH BANK", "Account Statement | 01 Mar - 31 Mar 2026")
    
    y = 160
    draw_field(draw, 40, y, "Account Holder:", "John Smith"); y += 35
    draw_field(draw, 40, y, "BSB:", "063-109"); y += 35
    draw_field(draw, 40, y, "Account Number:", "1234 5678"); y += 35
    draw_field(draw, 40, y, "Opening Balance:", "$12,450.00"); y += 50
    
    # Transactions
    draw.text((40, y), "TRANSACTIONS", fill=HEADER_COLOR, font=get_font(18)); y += 35
    cols = ["Date", "Description", "Debit", "Credit"]
    widths = [120, 300, 140, 140]
    draw_table_header(draw, 40, y, cols, widths); y += 36
    
    transactions = [
        ("01 Mar", "Opening Balance", "", "$12,450.00"),
        ("03 Mar", "Woolworths", "$85.40", ""),
        ("05 Mar", "Salary - ABC PTY LTD", "", "$5,102.80"),
        ("07 Mar", "Rent Payment", "$1,800.00", ""),
        ("10 Mar", "Transfer to Savings", "$500.00", ""),
        ("12 Mar", "Netflix Subscription", "$22.99", ""),
        ("15 Mar", "Salary - ABC PTY LTD", "", "$5,102.80"),
        ("18 Mar", "Electricity Bill", "$156.30", ""),
        ("20 Mar", "Groceries - Coles", "$120.45", ""),
        ("22 Mar", "Insurance Premium", "$210.00", ""),
        ("25 Mar", "ATM Withdrawal", "$200.00", ""),
        ("28 Mar", "Phone Bill", "$65.00", ""),
    ]
    
    for txn in transactions:
        draw_table_row(draw, 40, y, txn, widths, highlight=bool(txn[3]))
        y += 31
    
    y += 15
    draw.rectangle([(40, y), (WIDTH - 40, y + 50)], fill=(230, 240, 255))
    draw.text((60, y + 12), "CLOSING BALANCE:", fill=HEADER_COLOR, font=get_font(20))
    draw.text((500, y + 12), "$19,494.26", fill=HEADER_COLOR, font=get_font(22))
    
    img.save(SAMPLE_DIR / "sample_bank_statement.png")
    print("✅ Generated: sample_bank_statement.png")


# ─── Tax Return ───────────────────────────────────────────────────────────

def generate_tax_return():
    img = Image.new("RGB", (WIDTH, HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(img)
    
    draw_header(draw, "AUSTRALIAN TAX RETURN", "Financial Year 2025-2026 | Australian Taxation Office")
    
    y = 160
    draw_field(draw, 40, y, "Taxpayer Name:", "John Robert Smith"); y += 35
    draw_field(draw, 40, y, "TFN:", "123 456 789"); y += 35
    draw_field(draw, 40, y, "Date of Birth:", "15/06/1990"); y += 35
    draw_field(draw, 40, y, "ABN (if applicable):", "51 824 753 556"); y += 50
    
    draw.text((40, y), "INCOME", fill=HEADER_COLOR, font=get_font(18)); y += 35
    cols = ["Income Type", "", "Label", "Amount"]
    widths = [250, 80, 80, 200]
    draw_table_header(draw, 40, y, cols, widths); y += 36
    draw_table_row(draw, 40, y, ["Salary and Wages", "", "L1", "$96,480.00"], widths); y += 31
    draw_table_row(draw, 40, y, ["Interest Income", "", "L2", "$342.50"], widths); y += 31
    draw_table_row(draw, 40, y, ["Dividend Income", "", "L3", "$1,250.00"], widths); y += 31
    draw_table_row(draw, 40, y, ["Rental Income", "", "L4", "$18,000.00"], widths, highlight=True); y += 40
    
    draw.text((400, y), "Total Income:", fill=TEXT_COLOR, font=get_font(16))
    draw.text((560, y), "$116,072.50", fill=ACCENT_COLOR, font=get_font(18)); y += 50
    
    draw.text((40, y), "DEDUCTIONS", fill=(180, 40, 40), font=get_font(18)); y += 35
    draw_table_header(draw, 40, y, ["Deduction Type", "", "Label", "Amount"], widths); y += 36
    draw_table_row(draw, 40, y, ["Work-Related Expenses", "", "D1", "$3,420.00"], widths); y += 31
    draw_table_row(draw, 40, y, ["Rental Property Expenses", "", "D2", "$6,800.00"], widths); y += 31
    draw_table_row(draw, 40, y, ["Donations", "", "D3", "$500.00"], widths); y += 40
    
    draw.text((400, y), "Total Deductions:", fill=TEXT_COLOR, font=get_font(16))
    draw.text((560, y), "$10,720.00", fill=(180, 40, 40), font=get_font(18)); y += 50
    
    # Taxable income
    draw.rectangle([(40, y), (WIDTH - 40, y + 50)], fill=(255, 245, 230))
    draw.text((60, y + 12), "TAXABLE INCOME:", fill=HEADER_COLOR, font=get_font(20))
    draw.text((500, y + 12), "$105,352.50", fill=HEADER_COLOR, font=get_font(22))
    
    img.save(SAMPLE_DIR / "sample_tax_return.png")
    print("✅ Generated: sample_tax_return.png")


# ─── Driver's License ─────────────────────────────────────────────────────

def generate_drivers_license():
    img = Image.new("RGB", (WIDTH, HEIGHT), (230, 240, 250))
    draw = ImageDraw.Draw(img)
    
    # Header
    draw.rectangle([(0, 0), (WIDTH, 100)], fill=(0, 50, 100))
    draw.text((40, 20), "DRIVER LICENCE", fill=(255, 255, 255), font=get_font(32))
    draw.text((40, 60), "State of New South Wales", fill=(180, 200, 255), font=get_font(16))
    
    # Photo placeholder
    draw.rectangle([(40, 130), (220, 350)], fill=(200, 200, 200), outline=(150, 150, 150))
    draw.text((80, 220), "PHOTO", fill=(120, 120, 120), font=get_font(24))
    
    y = 150
    draw_field(draw, 250, y, "Licence No:", "12345678"); y += 40
    draw_field(draw, 250, y, "Surname:", "SMITH"); y += 40
    draw_field(draw, 250, y, "Given Names:", "JOHN ROBERT"); y += 40
    draw_field(draw, 250, y, "Date of Birth:", "15/06/1990"); y += 40
    draw_field(draw, 250, y, "Address:", "42 Wallaby Way"); y += 35
    draw.text((450, y), "Sydney NSW 2000", fill=TEXT_COLOR, font=get_font(14)); y += 40
    draw_field(draw, 250, y, "Licence Class:", "C"); y += 40
    draw_field(draw, 250, y, "Expiry Date:", "15/06/2031"); y += 60
    
    # Card number
    draw.rectangle([(40, y), (WIDTH - 40, y + 60)], fill=(240, 240, 240))
    draw.text((60, y + 15), "Card Number: DL-NSW-2026-0847-ABCD", fill=TEXT_COLOR, font=get_font(18))
    
    img.save(SAMPLE_DIR / "sample_drivers_license.png")
    print("✅ Generated: sample_drivers_license.png")


# ─── Invoice ──────────────────────────────────────────────────────────────

def generate_invoice():
    img = Image.new("RGB", (WIDTH, HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(img)
    
    draw_header(draw, "TAX INVOICE", "Invoice #INV-2026-0342")
    
    y = 150
    draw.text((40, y), "FROM:", fill=(100, 100, 100), font=get_font(14)); y += 25
    draw.text((40, y), "TechSolutions Australia Pty Ltd", fill=TEXT_COLOR, font=get_font(18)); y += 25
    draw.text((40, y), "ABN: 93 123 456 789", fill=TEXT_COLOR, font=get_font(14)); y += 20
    draw.text((40, y), "456 Collins Street, Melbourne VIC 3000", fill=TEXT_COLOR, font=get_font(14)); y += 40
    
    draw.text((40, y), "TO:", fill=(100, 100, 100), font=get_font(14)); y += 25
    draw.text((40, y), "ABC Pty Ltd", fill=TEXT_COLOR, font=get_font(18)); y += 25
    draw.text((40, y), "ABN: 51 824 753 556", fill=TEXT_COLOR, font=get_font(14)); y += 20
    draw.text((40, y), "789 George Street, Sydney NSW 2000", fill=TEXT_COLOR, font=get_font(14)); y += 40
    
    draw_field(draw, 40, y, "Invoice Date:", "15 March 2026"); y += 35
    draw_field(draw, 40, y, "Due Date:", "14 April 2026"); y += 50
    
    # Line items
    cols = ["Description", "Qty", "Unit Price", "Amount"]
    widths = [350, 80, 130, 140]
    draw_table_header(draw, 40, y, cols, widths); y += 36
    draw_table_row(draw, 40, y, ["Software Development Services", "120", "$150.00", "$18,000.00"], widths); y += 31
    draw_table_row(draw, 40, y, ["UI/UX Design Consultation", "40", "$120.00", "$4,800.00"], widths); y += 31
    draw_table_row(draw, 40, y, ["Project Management", "20", "$130.00", "$2,600.00"], widths); y += 31
    draw_table_row(draw, 40, y, ["Cloud Infrastructure (Monthly)", "1", "$450.00", "$450.00"], widths); y += 45
    
    # Totals
    draw.text((400, y), "Subtotal:", fill=TEXT_COLOR, font=get_font(16))
    draw.text((560, y), "$25,850.00", fill=TEXT_COLOR, font=get_font(16)); y += 30
    draw.text((400, y), "GST (10%):", fill=TEXT_COLOR, font=get_font(16))
    draw.text((560, y), "$2,585.00", fill=TEXT_COLOR, font=get_font(16)); y += 35
    
    draw.rectangle([(380, y), (WIDTH - 40, y + 50)], fill=(230, 245, 230))
    draw.text((400, y + 12), "TOTAL:", fill=HEADER_COLOR, font=get_font(20))
    draw.text((540, y + 12), "$28,435.00", fill=ACCENT_COLOR, font=get_font(22))
    
    img.save(SAMPLE_DIR / "sample_invoice.png")
    print("✅ Generated: sample_invoice.png")


# ─── Utility Bill ─────────────────────────────────────────────────────────

def generate_utility_bill():
    img = Image.new("RGB", (WIDTH, HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(img)
    
    draw_header(draw, "ENERGY AUSTRALIA", "Electricity Account Statement")
    
    y = 160
    draw_field(draw, 40, y, "Account Number:", "EA-8834721"); y += 35
    draw_field(draw, 40, y, "Customer Name:", "John Smith"); y += 35
    draw_field(draw, 40, y, "Service Address:", "42 Wallaby Way, Sydney NSW 2000"); y += 35
    draw_field(draw, 40, y, "Billing Period:", "01 Feb 2026 - 28 Feb 2026"); y += 35
    draw_field(draw, 40, y, "Issue Date:", "05 Mar 2026"); y += 50
    
    draw.text((40, y), "USAGE SUMMARY", fill=HEADER_COLOR, font=get_font(18)); y += 40
    
    draw_field(draw, 40, y, "Previous Reading:", "45,230 kWh"); y += 35
    draw_field(draw, 40, y, "Current Reading:", "45,580 kWh"); y += 35
    draw_field(draw, 40, y, "Usage This Period:", "350 kWh"); y += 50
    
    draw.text((40, y), "CHARGES", fill=HEADER_COLOR, font=get_font(18)); y += 35
    cols = ["Description", "", "", "Amount"]
    widths = [250, 80, 80, 200]
    draw_table_header(draw, 40, y, cols, widths); y += 36
    draw_table_row(draw, 40, y, ["Supply Charge (28 days)", "", "", "$30.52"], widths); y += 31
    draw_table_row(draw, 40, y, ["Usage Charge (350 kWh)", "", "", "$98.70"], widths); y += 31
    draw_table_row(draw, 40, y, ["Green Energy Contribution", "", "", "$5.00"], widths); y += 31
    draw_table_row(draw, 40, y, ["GST", "", "", "$13.42"], widths); y += 45
    
    draw.rectangle([(40, y), (WIDTH - 40, y + 50)], fill=(255, 240, 230))
    draw.text((60, y + 12), "TOTAL DUE:", fill=(180, 40, 40), font=get_font(20))
    draw.text((500, y + 12), "$147.64", fill=(180, 40, 40), font=get_font(22))
    y += 60
    draw.text((40, y), "Due Date: 25 March 2026", fill=TEXT_COLOR, font=get_font(14))
    
    img.save(SAMPLE_DIR / "sample_utility_bill.png")
    print("✅ Generated: sample_utility_bill.png")


# ─── Main ─────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("Generating sample documents...")
    generate_payslip()
    generate_bank_statement()
    generate_tax_return()
    generate_drivers_license()
    generate_invoice()
    generate_utility_bill()
    print(f"\n✅ All samples saved to: {SAMPLE_DIR}")
    print(f"   Total files: {len(list(SAMPLE_DIR.glob('*.png')))}")
