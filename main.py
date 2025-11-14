from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.core.window import Window
from kivy.lang import Builder
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.menu import MDDropdownMenu
from datetime import date, datetime
from pdf_generator import FamilyPDFGenerator
from expenditurereport import PDFGenerator
from contactreport import ContactPDFGenerator
from kivymd.uix.dialog import (
    MDDialog,
    MDDialogHeadlineText,
    MDDialogSupportingText,
    MDDialogButtonContainer,
    MDDialogContentContainer,
)

from kivy.utils import get_color_from_hex
from kivy.utils import platform
import sqlite3, os, shutil
from kivy.graphics import Color, Rectangle
from kivymd.uix.snackbar import MDSnackbar, MDSnackbarText
from kivy.uix.filechooser import FileChooserListView
from kivy.clock import Clock
import subprocess
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.modalview import ModalView
from kivy.uix.popup import Popup
from kivy.uix.widget import Widget
# Optional: for mobile permission handling
if platform == "android":
    from android.permissions import request_permissions, Permission
    from android.storage import app_storage_path, primary_external_storage_path
    request_permissions([Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE])
Window.clearcolor = (1, 1, 1, 1)
for kv in ["topbar.kv", "database.kv","homescreen.kv", "registerfamily.kv","memberfamily.kv","accounting.kv","expense.kv","meeting.kv"]:
    Builder.load_file(kv)  # 🔹 Load the new screen

class DialogManager:
    dialog = None

    @classmethod
    def show_dialog(cls, title, message, color="default"):
        """Reusable dialog for KivyMD 2.0.1.dev0."""
        color_map = {
            "success": "#4CAF50",
            "error": "#E53935",
            "info": "#2196F3",
            "default": "#424242",
        }

        bg_color = get_color_from_hex(color_map.get(color, "#424242"))

        # Close existing dialog if open
        if cls.dialog:
            cls.dialog.dismiss()

        # ✅ New-style MDDialog definition
        cls.dialog = MDDialog(
            MDDialogHeadlineText(text=title),
            MDDialogSupportingText(text=message),
            MDDialogButtonContainer(
                MDButton(
                    MDButtonText(text="OK"),
                    on_release=lambda x: cls.dialog.dismiss(),
                ),
            ),
            md_bg_color=bg_color,
        )

        cls.dialog.open()
class DatabaseSetupScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()

    def build_ui(self):
        grid = self.ids.database_grid
        grid.clear_widgets()

        layout = MDBoxLayout(
            orientation="vertical",
            spacing="20dp",
            padding="20dp",
            adaptive_height=True
        )

        title = MDLabel(
            text="Database Setup",
            halign="center",
            theme_text_color="Primary",
        )

        create_btn = MDButton(
            style="filled",
            on_release=self.create_database,
            size_hint=(None, None),
            width="300dp",
            height="50dp",
            pos_hint={"center_x": 0.5},
            
        )
        create_btn.add_widget(MDButtonText(text="Create New Database", halign="center", theme_text_color="Custom"))

        upload_btn = MDButton(
            style="outlined",
            on_release=self.upload_backup,
            size_hint=(None, None),
            size=("250dp", "50dp"),
            pos_hint={"center_x": 0.5},
            
        )
        upload_btn.add_widget(MDButtonText(text="Upload Backup", halign="center", theme_text_color="Primary"))

        layout.add_widget(title)
        layout.add_widget(create_btn)
        layout.add_widget(upload_btn)

        grid.add_widget(layout)

    def get_backup_folder(self):
        """Return a valid backup folder based on platform."""
        if platform == "android":
            try:
                from android.storage import primary_external_storage_path, app_storage_path
                base_path = primary_external_storage_path()
                folder = os.path.join(base_path, "ChamaApp", "Backups")
            except Exception:
                folder = os.path.join(app_storage_path(), "Backups")
        else:
            folder = os.path.join(os.path.expanduser("~"), "ChamaApp", "Backups")
        os.makedirs(folder, exist_ok=True)
        return folder

    def create_database(self, *args):
        """Create family.db and the tables, then let the app continue."""
        db_name = "family.db"

        try:
            if not os.path.exists(db_name):
                conn = sqlite3.connect(db_name)
                cursor = conn.cursor()

                # Create tables
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS family (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        family_name TEXT NOT NULL
                    )
                """)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS member (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        family_name TEXT NOT NULL,
                        firstname TEXT NOT NULL,
                        middlename TEXT NOT NULL,
                        lastname TEXT NOT NULL,
                        phone TEXT NOT NULL
                    )
                """)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS accounts (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        family_name TEXT NOT NULL,
                        fullnames TEXT NOT NULL,
                        accounttype TEXT NOT NULL,
                        amount TEXT NOT NULL,
                        paid_on TEXT 
                    )
                """)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS expenses (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        family_name TEXT NOT NULL,
                        fullnames TEXT NOT NULL,
                        accounttype TEXT NOT NULL,
                        amount TEXT NOT NULL,
                        paid_on  TEXT
                    )
                """)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS meeting (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        meeting_date TEXT NOT NULL,
                        residence TEXT NOT NULL
                    )
                """)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS tea_kitty (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        family_name TEXT NOT NULL,
                        fullnames TEXT NOT NULL,
                        residence TEXT NOT NULL,
                        amount_due REAL NOT NULL,
                        meeting_date TEXT NOT NULL,
                        amount_paid REAL,
                        status TEXT DEFAULT 'unpaid',
                        paid_on TEXT 
                    )
                """)

                conn.commit()
                conn.close()
                DialogManager.show_dialog("✅ Success", "Family database created successfully!", color="success")
            else:
                DialogManager.show_dialog("ℹ️ Info", "Database already exists!", color="info")

            # Tell the app to finish DB setup and continue
            app = MDApp.get_running_app()
            Clock.schedule_once(lambda dt: app.post_db_init(), 0.2)

        except Exception as e:
            DialogManager.show_dialog("❌ Error", str(e), color="error")

    def upload_backup(self, *args):
        start_path = "/storage/emulated/0/" if platform == "android" else os.path.expanduser("~")
        filechooser = FileChooserListView(
            path=start_path,
            filters=["*.db"],
            size_hint=(1, None),
            height="320dp"
        )

        # Main vertical content
        content = MDBoxLayout(orientation="vertical", spacing=8, padding=8)
        content.add_widget(filechooser)

        # Buttons row (centered)
        btn_row = AnchorLayout(size_hint=(1, None), height="48dp")
        inner = MDBoxLayout(size_hint=(None, None), size=("260dp", "48dp"), spacing=8)

        cancel_btn = MDButton(MDButtonText(text="Cancel"), size_hint=(None, None), size=("120dp", "44dp"))
        restore_btn = MDButton(MDButtonText(text="Restore Selected"), size_hint=(None, None), size=("140dp", "44dp"))

        inner.add_widget(cancel_btn)
        inner.add_widget(restore_btn)
        btn_row.add_widget(inner)
        content.add_widget(btn_row)

        popup = Popup(
            title="📂 Select Database File",
            content=content,
            size_hint=(0.95, None),
            height="460dp",
            auto_dismiss=False
        )

        def do_restore(instance):
            sel = filechooser.selection
            if not sel:
                DialogManager.show_dialog("Info", "No file selected", color="info")
                return
            selected_path = sel[0]
            try:
                dest_db = os.path.join(os.getcwd(), "family.db")
                shutil.copy2(selected_path, dest_db)

                DialogManager.show_dialog("✅ Success", f"Restored backup to:\n{dest_db}", color="success")

                app = MDApp.get_running_app()
                Clock.schedule_once(lambda dt: app.post_db_init(), 0.2)

                popup.dismiss()
            except Exception as e:
                DialogManager.show_dialog("❌ Error", str(e), color="error")

        def do_cancel(instance):
            popup.dismiss()

        restore_btn.bind(on_release=do_restore)
        cancel_btn.bind(on_release=do_cancel)

        popup.open()
class HomeScreen(MDScreen):
    # def __init__(self, **kwargs):
    #     super().__init__(**kwargs)
    #     Clock.schedule_once(self.load_families, 1.5)
    #     # self.families = db.get_families()

    def on_enter(self):
        app = MDApp.get_running_app()
        grid = self.ids.family_grid
        grid.clear_widgets()
        try:
            families = db.get_families()
        except Exception as e:
            DialogManager.show_dialog("Error", str(e), color="error")
            return

        for family in families:
            card = MDCard(
                style="elevated",
                size_hint=(1, None),
                height="180dp",
                radius=[20],
                md_bg_color=(0.95, 0.95, 1, 1),
                padding="16dp",
                elevation=6,
            )

            box = MDBoxLayout(orientation="vertical", spacing="20dp", adaptive_height=True)
            box.add_widget(MDLabel(text=str(family["Family Name"]), halign="center", theme_text_color="Custom"))
            box.add_widget(MDLabel(text=f"Total Amount = {str(family['Total'])}", halign="center"))

            btn = MDButton(
                style="filled",
                md_bg_color=(0.2, 0.6, 1, 1),
                size_hint=(None, None),
                width="300dp",
                height="50dp",
                pos_hint={"center_x": 0.5},
                on_release=lambda btn, f=family["Family Name"]: self.view_family(f),
            )
            btn.add_widget(MDButtonText(text="View Members", halign="center", text_color=(1, 1, 1, 1)))
            box.add_widget(btn)

            card.add_widget(box)
            grid.add_widget(card)

    def view_family(self, name):
        DialogManager.show_dialog("Info", f"Selected family: {name}", color="info")


class MeetingScreen(MDScreen):
    def reset_form(self):
        self.ids.residence.text=""
        self.ids.cateringamount.text=""
    def register_meeting(self,residence, cateringamount):
        today = date.today()
        formatted_date = today.strftime("%d/%B/%Y")
        if residence=='':
            DialogManager.show_dialog("Input Error","Venue Is Required", color='error')
        elif cateringamount=='':
            DialogManager.show_dialog("Input Error", "Catering Amount Is Required", color='error')
        else:
            result=db.add_meeting(formatted_date, residence,cateringamount)
            if result is True:
                DialogManager.show_dialog("Success","Meeting Registered Successfully", color="success")
                self.reset_form()
            elif result is False:
                DialogManager.show_dialog("Info","An error has occured", color="info")
            elif result=='0':
                DialogManager.show_dialog("Info","Register Family", color="info")
            else:
                DialogManager.show_dialog("Error","Unknown Error Has Occured", color="error")
class RegisterFamilyScreen(MDScreen):
    def reset_form(self):
        """Clear all text fields."""
        self.ids.family_name.text = "" 
    def register_family(self,familyname):
        if familyname=="":
            title="Input Error"
            message="Family Name Is Required"
            DialogManager.show_dialog(title, message,color="error") 
        else:
            if db.add_family(familyname)==True:
                title="Success"
                message="Family Name Added Successfully"
                DialogManager.show_dialog(title, message,color="success")
                self.reset_form()
            else:
                title="Error"
                message="An Error Has Occurred"
                DialogManager.show_dialog(title, message, color="error")
class MembersFamilyScreen(MDScreen):
    def reset_form(self):
        """Clear all text fields."""
        self.ids.contribution_field.text=""
        self.ids.firstname.text=""
        self.ids.middlename.text=""
        self.ids.lastname.text=""
        self.ids.phoneno.text=""
    def on_enter(self):
        # Create dropdown menu items
        families= db.get_families()
        # ✅ Use MDMenuItem (not MenuItem)

        menu_items = [
            {
                "text": str(name["Family Name"]),
                "on_release": lambda x=str(name["Family Name"]): self.set_account(x),
            }
            for name in families
        ]

        self.menu = MDDropdownMenu(
            caller=self.ids.contribution_field,
            items=menu_items,
            position="bottom", 
            width_mult=4,
        )
    def family_member(self,contribution_field, firstname,middlename, lastname, phoneno):
        if contribution_field=="":
            DialogManager.show_dialog("Input Error", "Choose Family", color="error")
        elif firstname=="":
            DialogManager.show_dialog("Input Error","First Name Is Required", color="error")
        elif middlename=="":
            DialogManager.show_dialog("Input Error", "middlename Is Required", color="error")
        elif lastname=="":
            DialogManager.show_dialog("Input Error", "Last Name Is Required", color="error")
        elif phoneno=="":
            DialogManager.show_dialog("Input Error", "Phone Number Is Reuired", color="error")
        else:    
            if db.add_member(contribution_field, firstname,middlename, lastname, phoneno)==True:
                DialogManager.show_dialog("Success","Family Member Added Successfully", color="success")
                self.reset_form()
            else:
                DialogManager.show_dialog("Error","An Error Has Occured", color="success")
    def contact_report(self):
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"{timestamp}.pdf"
        output_file = ContactPDFGenerator.get_save_path(filename)
        location=lc.get_db_path()   
        pdf = ContactPDFGenerator(location,output_file)
        results=pdf.generate_pdf()
        DialogManager.show_dialog("Success",results,color="success")
    def open_contribution_menu(self):
        if hasattr(self, "menu"):
            self.menu.open()

    def set_account(self, account_name):
        self.ids.contribution_field.text = account_name
        #self.ids.selected_label.text = f"Selected: {account_name}"
        self.menu.dismiss()
class AccountingScreen(MDScreen):
    def on_enter(self):
        """Called when the screen is entered."""
        # Load family dropdown first
        families = db.get_families()
        family_menu_items = [
            {
                "text": str(name["Family Name"]),
                "on_release": lambda x=str(name["Family Name"]): self.set_family(x),
            }
            for name in families
        ]

        self.family_menu = MDDropdownMenu(
            caller=self.ids.family_name,
            items=family_menu_items,
            position="bottom",
            width_mult=4,
        )

        # Initially, member dropdown is empty
        self.member_menu = MDDropdownMenu(
            caller=self.ids.family_member,
            items=[],
            position="bottom",
            width_mult=4,
        )

        # Accounts menu stays static
        accounts = ["Main Account", "Petty Account", "Tea Kitty"]
        account_menu_items = [
            {"text": name, "on_release": lambda x=name: self.set_account(x)}
            for name in accounts
        ]

        self.account_menu = MDDropdownMenu(
            caller=self.ids.account_name,
            items=account_menu_items,
            position="bottom",
            width_mult=4,
        )

    def open_family_menu(self):
        self.family_menu.open()

    def set_family(self, family_name):
        """When a family is selected, update the member dropdown."""
        self.ids.family_name.text = family_name
        self.family_menu.dismiss()

        # Fetch members for this family
        members = db.get_members_by_family(family_name)
        member_names = [f"{m[0]} {m[1]} {m[2]}" for m in members] if members else []


        # Create new menu items for members
        member_menu_items = [
        {"text": str(name), "on_release": lambda x=str(name): self.set_member(x)}
            for name in member_names
        ]
        self.member_menu.items = member_menu_items

    def open_member_menu(self):
        if hasattr(self, "member_menu"):
            self.member_menu.open()

    def set_member(self, name):
        self.ids.family_member.text = name
        self.member_menu.dismiss()

    def open_account_menu(self):
        if hasattr(self, "account_menu"):
            self.account_menu.open()

    def set_account(self, name):
        self.ids.account_name.text = name
        self.account_menu.dismiss()
    def reset_form(self):
        self.ids.family_name.text=""
        self.ids.family_member.text=""
        self.ids.account_name.text=""
        self.ids.amount.text=""
    def family_record(self, family_name, family_member,account_name,amount):
        if family_name=="":
            DialogManager.show_dialog("Error", "Select Family Name", color="error")
        elif family_member=="":
            DialogManager.show_dialog("Error", "Select Family Member", color="error")
        elif account_name=="":
            DialogManager.show_dialog("Error", "Select Account Type", color="error")
        elif amount=="":
            DialogManager.show_dialog("Error", "Amount Is Required", color="error")
        else:
            result=db.add_record(family_name, family_member,account_name,amount)
            DialogManager.show_dialog("info",result, color="info")
            self.reset_form()
    def generate_reports(self):
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"{timestamp}.pdf"
        output_file = FamilyPDFGenerator.get_save_path(filename) 
        location=lc.get_db_path()  
        pdf = FamilyPDFGenerator(location,output_file)
        response=pdf.generate_pdf()
        DialogManager.show_dialog("Success",response, color="success")
class ExpenditureScreen(MDScreen):
    def on_enter(self):
        accounts=[
            "Main Account",
            "Petty Account",
        ]
        account_menu_items=[
            {
                "text": name,
                "on_release": lambda x=name: self.set_account(x),
            }
            for name in accounts
        ]
        self.account_menu = MDDropdownMenu(
            caller=self.ids.account_name,
            items=account_menu_items,
            position="bottom",
            width_mult=4,
        )
    def open_account_menu(self):
        if hasattr(self, "account_menu"):
            self.account_menu.open()

    def set_account(self, name):
        self.ids.account_name.text = name
        self.account_menu.dismiss()
    def reset_form(self):
        self.ids.beneficially.text=""
        self.ids.expense_description.text=""
        self.ids.account_name.text=""
        self.ids.amount.text=""
    def family_expense(self, beneficially,expense_description,account_name,amount):
        if beneficially=="":
            DialogManager.show_dialog("Error", "Beneficiary Name Is Required", color="error")
        elif expense_description=="":
            DialogManager.show_dialog("Error", "Expense Description Is Required", color="error")
        elif account_name=="":
            DialogManager.show_dialog("Error","Select Acount Type", color="error")
        elif amount=="":
            DialogManager.show_dialog("Error", "Amount Is Required", color="error")
        else:
            result = db.add_expenses(beneficially, expense_description, account_name, amount)
            DialogManager.show_dialog("info", result, color="info")
            self.reset_form()
    def expense_report(self):
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"{timestamp}.pdf"
        output_file = PDFGenerator.get_save_path(filename)
        location=lc.get_db_path()  
        pdf = PDFGenerator(location,output_file)
        res=pdf.generate_pdf()
        DialogManager.show_dialog("Info",res,color="info")
class FamilyFintechApp(MDApp):    
    db=None
    def build(self):
        # do not import or create Database() here
        self.theme_cls.theme_style = "Light"
        self.sm = MDScreenManager()

        # create screen instances (do not trigger DB work here)
        self.db_screen = DatabaseSetupScreen()
        self.home_screen = HomeScreen()
        self.register_screen = RegisterFamilyScreen()
        self.members_screen = MembersFamilyScreen()
        self.account_screen = AccountingScreen()
        self.expenditure_screen = ExpenditureScreen()
        self.meeting_screen = MeetingScreen()

        # add to manager (use the names your kv expects; adjust if needed)
        self.sm.add_widget(self.db_screen)
        self.sm.add_widget(self.home_screen)
        self.sm.add_widget(self.register_screen)
        self.sm.add_widget(self.members_screen)
        self.sm.add_widget(self.account_screen)
        self.sm.add_widget(self.expenditure_screen)
        self.sm.add_widget(self.meeting_screen)

        menu_items = [
            {"text": "Home", "on_release": lambda: self.change_screen("home")},
            {"text": "Register Family", "on_release": lambda: self.change_screen("register_family")},
            {"text": "Register Meeting", "on_release": lambda: self.change_screen("meeting")},
            {"text": "Family Member", "on_release": lambda: self.change_screen("members_family")},
            {"text":"Accounts", "on_release":lambda:self.change_screen("accounts")},
            {"text":"Expenditure", "on_release":lambda:self.change_screen("expenses")},
        ]
        self.menu = MDDropdownMenu(items=menu_items, width_mult=4)

        return self.sm

    def on_start(self):
        # run the DB check after the UI is built
        Clock.schedule_once(lambda dt: self.check_database_on_startup(), 0.1)

    def check_database_on_startup(self):
        """Check if database exists. If not, show setup screen; otherwise, load DB."""
        global db
        global lc
        import os
        from kivy.utils import platform

        db_name = "family.db"

        # Determine backup directory
        if platform == "android":
            from android.storage import primary_external_storage_path
            backup_dir = os.path.join(primary_external_storage_path(), "ChamaApp", "Backups")
        else:
            backup_dir = os.path.join(os.path.expanduser("~"), "ChamaApp", "Backups")

        os.makedirs(backup_dir, exist_ok=True)

        # --- KEY FIX STARTS HERE ---
        if os.path.exists(db_name):
            # Import ONLY after confirming DB exists
            from const import Database, Databaselocation
            db = Database()
            lc=Databaselocation()
            self.sm.current = "home"
        else:
            # Database does not exist → show the setup screen
            self.sm.current = "setup"

    def post_db_init(self):
        """Import Database class now that family.db exists, instantiate it as global db,
           then switch to home and allow the rest of the app to use db."""
        global db
        global lc
        # only import when DB exists to avoid early connection attempts
        from const import Database,Databaselocation
        try:
            db = Database()
            lc=Databaselocation()
        except Exception as e:
            DialogManager.show_dialog("❌ Error", f"Failed to initialize database: {e}", color="error")
            # keep user on setup screen so they can retry
            self.sm.current = "database_setup"
            return

        # DB initialized — go to home screen
        self.sm.current = "home"

    def open_menu(self, caller):
        self.menu.caller = caller
        self.menu.open()

    def back_up(self):
        # make sure db is ready
        if db is None:
            DialogManager.show_dialog("Info", "Database not ready", color="info")
            return
        result = db.backup_database()
        DialogManager.show_dialog("Info", result, color="info")

    def change_screen(self, screen_name):
        self.sm.current = screen_name
        try:
            self.menu.dismiss()
        except Exception:
            pass

if __name__ == "__main__":
    FamilyFintechApp().run()
    