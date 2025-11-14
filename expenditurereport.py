import sqlite3
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
import os
from kivy.utils import platform

class PDFGenerator:
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

    def fetch_expense_data(self):
        """Get account data for each family."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT family_name, fullnames, accounttype, paid_on, amount
            FROM expenses
            ORDER BY paid_on ASC
        """)
        rows = cursor.fetchall()
        conn.close()
        return rows if rows else []

    def generate_pdf(self):
        """Generate a colorful PDF with wrapped text."""
        doc = SimpleDocTemplate(self.output_file, pagesize=A4)
        styles = getSampleStyleSheet()

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

        cell_style = ParagraphStyle(
            'Cell',
            parent=styles['Normal'],
            fontSize=10,
            leading=12,
            alignment=0,  # left alignment
        )

        table_widths = [100, 200, 70, 100, 70]
        accounts = self.fetch_expense_data()

        content = []
        content.append(Paragraph("Expenditure Report", title_style))
        content.append(Spacer(1, 20))

        if accounts:
            data = [["Beneficiary", "Reason", "Account Type", "Paid On", "Amount (Ksh)"]]
            total_amount = 0

            for family_name,fullname, accounttype, paid_on, amount in accounts:
                row = [
                    Paragraph(family_name, cell_style),
                    Paragraph(fullname, cell_style),
                    Paragraph(accounttype, cell_style),
                    Paragraph(str(paid_on), cell_style),
                    Paragraph(f"{int(amount):,}", cell_style)
                ]
                data.append(row)
                total_amount += int(amount)

            data.append([
                "", "", "", Paragraph("<b>Total:</b>", cell_style),
                Paragraph(f"<b>{total_amount:,.2f}</b>", cell_style)
            ])

            table = Table(data, colWidths=table_widths)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#4CAF50")),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
                ('BACKGROUND', (0, 1), (-1, -2), colors.HexColor("#E8F5E9")),
                ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor("#C8E6C9")),
                ('TEXTCOLOR', (0, -1), (-1, -1), colors.HexColor("#1B5E20")),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ]))

            content.append(table)
        else:
            content.append(Paragraph("<font color='red'>No account records found.</font>", styles['Normal']))

        doc.build(content)
        return(f"✅ PDF generated successfully: {self.output_file}")
    def get_save_path(filename):
        if platform == "android":
            base = "/storage/emulated/0/Documents/ChamaReports"
        else:
            base = os.path.join(os.getcwd(), "ChamaReports")

        if not os.path.exists(base):
            os.makedirs(base)

        return os.path.join(base, filename)