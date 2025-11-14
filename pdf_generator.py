import sqlite3
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from datetime import date, datetime,timedelta, timezone
import os
from kivy.utils import platform
KENYA_TZ = timezone(timedelta(hours=3))
current_time = datetime.now(KENYA_TZ)
class FamilyPDFGenerator:
    """Fetch family and account data from the database, then generate a colorful PDF report."""

    def __init__(self, db_path, output_file):
        self.db_path = db_path
        self.output_file = output_file
    @staticmethod
    def get_save_path(filename):
        """Works on both Android and Desktop."""
        if platform == "android":
            base = "/storage/emulated/0/Documents/ChamaReports"
        else:
            base = os.path.join(os.getcwd(), "ChamaReports")

        if not os.path.exists(base):
            os.makedirs(base)

        return os.path.join(base, filename)
    def fetch_family_names(self):
        """Get all family names from the 'family' table."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT family_name FROM family ORDER BY id ASC")
        rows = cursor.fetchall()

        conn.close()
        return [row[0] for row in rows] if rows else []

    def fetch_account_data(self, family_name):
        """Get account data for each family."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT fullnames, accounttype, amount, paid_on
            FROM accounts
            WHERE family_name = ?
            ORDER BY paid_on ASC
        """, (family_name,))
        rows = cursor.fetchall()
        conn.close()
        return rows if rows else []

    def fetch_tea_kitty_data(self, family_name):
        """Get tea kitty contributions for the given family."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT fullnames, Residence, meeting_date, status, amount_due, amount_paid
            FROM tea_kitty
            WHERE family_name = ?
            ORDER BY id ASC
        """, (family_name,))
        rows = cursor.fetchall()
        conn.close()
        return rows if rows else []

    def generate_pdf(self):
        """Create a colorful PDF showing all families and their account records."""
        family_names = self.fetch_family_names()

        if not family_names:
            print("⚠️ No family names found in the database.")
            return

        # --- Set up PDF ---
        doc = SimpleDocTemplate(self.output_file, pagesize=A4)
        styles = getSampleStyleSheet()

        # --- Styles ---
        title_style = ParagraphStyle(
            'Title',
            parent=styles['Heading1'],
            alignment=1,
            textColor=colors.white,
            backColor=colors.HexColor("#1565C0"),
            fontSize=20,
            leading=24,
            spaceAfter=20,
        )

        family_style = ParagraphStyle(
            'FamilyName',
            parent=styles['Heading2'],
            textColor=colors.HexColor("#0D47A1"),
            spaceBefore=10,
            spaceAfter=8,
        )

        tea_kitty_header = ParagraphStyle(
            'TeaKittyHeader',
            parent=styles['Heading3'],
            textColor=colors.white,
            backColor=colors.HexColor("#FF9800"),
            alignment=1,
            fontSize=13,
            spaceBefore=10,
            spaceAfter=6,
        )

        # --- Content starts here ---
        content = [Paragraph("🏠 Family Financial Report", title_style), Spacer(1, 20)]

        # Shared table width setup (for all tables)
        table_widths = [165, 130, 160, 115]  # total ~470 points (perfect fit on A4)
        table_widths1=[150, 150, 100, 100,70] 
        for i, family_name in enumerate(family_names, start=1):
            content.append(Paragraph(f"{i}. {family_name}", family_style))

            # --- Account Data Table ---
            accounts = self.fetch_account_data(family_name)
            if accounts:
                data = [["Full Name", "Account Type", "Paid On", "Amount (Ksh)"]]
                total_amount = 0
                for fullname, accounttype, amount, paid_on in accounts:
                    data.append([fullname, accounttype, paid_on, int(amount)])
                    total_amount += int(amount)
                data.append(["", "", "Total:", f"{total_amount:.2f}"])

                table = Table(data, colWidths=table_widths)
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#4CAF50")),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('BACKGROUND', (0, 1), (-1, -2), colors.HexColor("#E8F5E9")),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
                    ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor("#C8E6C9")),
                    ('TEXTCOLOR', (0, -1), (-1, -1), colors.HexColor("#1B5E20")),
                    ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                ]))
                content.append(table)
            else:
                content.append(Paragraph("<font color='red'>No account records found.</font>", styles['Normal']))

            # --- Tea Kitty Data Table ---
            tea_kitty_data = self.fetch_tea_kitty_data(family_name)
            content.append(Paragraph("🍵 Tea Kitty Contributions", tea_kitty_header))

            if tea_kitty_data:
                data = [["Full Name", "Venue", "Meeting Date", "Status", "Amount (Ksh)"]]
                total_tea =0
                amount_paid_total = 0
                for fullnames, residence, meeting_date, status, amount_due, amount_paid in tea_kitty_data:
                    data.append([fullnames, residence, meeting_date, status, int(amount_due)])
                    total_tea += int(amount_due)
                    if status == "paid":
                        amount_paid_total += amount_paid
                balance = total_tea - amount_paid_total
                data.append(["", "", "", "Total:", f"{total_tea:.2f}"])
                data.append(["", "", "", "Balance:", f"{balance:.2f}"])

                table = Table(data, colWidths=table_widths1)  # same width as accounts table
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#FF9800")),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
                    ('BACKGROUND', (0, 1), (-1, -2), colors.HexColor("#FFF3E0")),
                    ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor("#FFE0B2")),
                    ('TEXTCOLOR', (0, -1), (-1, -1), colors.HexColor("#E65100")),
                    ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                ]))
                content.append(table)
            else:
                content.append(Paragraph("<font color='red'>No tea kitty records found.</font>", styles['Normal']))

            content.append(Spacer(1, 25))

        # --- Build the final PDF ---
        doc.build(content)
        return(f"✅ PDF generated successfully: {self.output_file}")

   
# --- Run the script ---
