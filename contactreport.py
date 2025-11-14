import sqlite3
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
import os
from kivy.utils import platform

class ContactPDFGenerator:
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
    def fetch_family_names(self):
        """Get all family names from the 'family' table."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT family_name FROM family ORDER BY id ASC")
        rows = cursor.fetchall()

        conn.close()
        return [row[0] for row in rows] if rows else []

    def fetch_contact_data(self, family_name):
        """Get account data for each family."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT firstname, middlename, lastname, phone
            FROM member
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
        content = [Paragraph("🏠 Family Contacts Report", title_style), Spacer(1, 20)]

        # Shared table width setup (for all tables)
        table_widths = [165, 130, 160, 115]  # total ~470 points (perfect fit on A4)
        for i, family_name in enumerate(family_names, start=1):
            content.append(Paragraph(f"{i}. {family_name}", family_style))

            # --- Account Data Table ---
            accounts = self.fetch_contact_data(family_name)
            if accounts:
                data = [["First Name", "Middle Name", "Last Name", "Contacts"]]
                total_amount = 0
                for firstname, middlename, lastname, phone in accounts:
                    data.append([firstname, middlename, lastname, phone])

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