# store.py
import sqlite3
from datetime import date, datetime,timedelta, timezone
from kivy.utils import platform
import os
today = date.today()
formatted_date = today.strftime("%d/%B/%Y")
todaydate = datetime.strptime(formatted_date, "%d/%B/%Y")
class CurrentTime:
    def get_time(self):
        KENYA_TZ = timezone(timedelta(hours=3))
        current_time = datetime.now(KENYA_TZ)

        # If storing as REAL (Unix timestamp)
        timestamp_value = current_time.timestamp()

        # If storing as TEXT (ISO format)
        iso_value = current_time.strftime("%H:%M:%S %d-%m-%Y")
        return iso_value
class Databaselocation:
    @staticmethod
    def get_db_path():
        if platform == "android":
            from android.storage import app_storage_path
            import shutil

            app_dir = app_storage_path()
            db_path = os.path.join(app_dir, "family.db")

            if not os.path.exists(db_path):
                shutil.copy("family.db", db_path)

            return db_path

        # Desktop / Linux
        return "family.db"

class Database:
    def __init__(self, db_name=None):
        if db_name is None:
            db_name = Databaselocation.get_db_path()  
        self.db=db_name
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
    def add_family(self, family_name):
        try:
            self.cursor.execute("INSERT INTO family (family_name) VALUES (?)", (family_name,))
            self.conn.commit()
            return True
        except Exception as e:
            return False
    def add_member(self, family_name, firstname,middlename, lastname, phoneno):
        try:
            self.cursor.execute("INSERT INTO member (family_name,firstname,middlename,lastname,phone) VALUES (?,?,?,?,?)", (family_name,firstname,middlename,lastname,phoneno))
            self.conn.commit()
            return True
        except Exception as e:
            return False  
    def get_families(self):
        results=[]
        self.cursor.execute("SELECT * FROM family")
        family=self.cursor.fetchall()
        for fam in family:
            self.cursor.execute('SELECT SUM(amount) from accounts WHERE family_name=?',(fam[1],))
            total_balance = self.cursor.fetchone()[0] or 0
            results.append({
            "Family Name": f"{fam[1]}",
            "Total": total_balance
        })
        return results
    def get_members_by_family(self, family_name):
        self.cursor.execute("SELECT firstname, middlename, lastname FROM member WHERE family_name=?",(family_name,))
        return self.cursor.fetchall()
    def add_record(self,family_name, family_member,account_name,amount):
        status="unpaid"
        status1="Incomplete"
        status2="paid"
        time_value=CurrentTime().get_time()
        if account_name=='Tea Kitty':
            self.cursor.execute("SELECT * FROM tea_kitty WHERE family_name=? ORDER BY id ASC",(family_name,))
            result=self.cursor.fetchall()
            if result:
                total_amountdue=0
                amounts=int(amount)
                total=0
                for record in result:
                    meeting_date=datetime.strptime(record[5], "%d/%B/%Y")
                    record_id=record[0]
                    if record[7] in ('unpaid', status1):
                        if meeting_date<=todaydate:
                            if amounts==int(record[4]):
                                self.cursor.execute("UPDATE tea_kitty SET fullnames=?, amount_paid=?,status=?, paid_on=? WHERE family_name=? AND id=?",(family_member,amount,status2,time_value,family_name,record_id))
                                self.conn.commit()
                                self.cursor.execute("SELECT * FROM tea_kitty WHERE family_name=?",(family_name,))
                                confirm=self.cursor.fetchall()
                                for confirmation in confirm:
                                    if confirmation[7]==status2:
                                        total+=int(confirmation[6])
                                    total_amountdue+=int(confirmation[4])
                                balance=total_amountdue-total
                                response=f"Amount Paid for meeting held at {record[3]} on date {record[5]} total amount remaining {balance}"
                                return response
                            elif amounts<int(record[4]):
                                response=f"Amount {amounts} is insufficient you need to pay {record[4]}"
                                return response
                        else:
                            response="No Records Found"
                            return response
                    else:
                        response="Schedule Meeting And Catering Amount"
                        return response
        else:
            try:
                self.cursor.execute("INSERT INTO accounts (family_name,fullnames,accounttype,amount,paid_on) VALUES(?,?,?,?,?)",(family_name,family_member,account_name,amount,time_value))
                self.conn.commit()                
                response=f"Amount Paid {amount} on date{formatted_date}"
                return response
            except Exception as e:
                response="An Error Has Occurred"
                return response
    def add_meeting(self,formatted_date, residence,cateringamount):
        self.cursor.execute("SELECT family_name From family")
        familydata=self.cursor.fetchall()
        if familydata:
            try:
                for family_data in familydata:
                    self.cursor.execute("INSERT INTO tea_kitty(family_name,fullnames,Residence,amount_due,meeting_date) VALUES(?,?,?,?,?)",(family_data[0],family_data[0],residence,cateringamount,formatted_date))
                    self.conn.commit()
                self.cursor.execute("INSERT INTO meeting(meeting_date,residence) VALUES(?,?)", (formatted_date,residence))
                self.conn.commit()
                return True
            except Exception as e:
                return False
        else:
            response="0"
            return response
    def backup_database(self,db_path=None):
        try:
            if db_path is None:
                db_path = Databaselocation.get_db_path()

            if platform == "android":
                from android.storage import primary_external_storage_path
                from android.permissions import request_permissions, Permission

                request_permissions([
                    Permission.WRITE_EXTERNAL_STORAGE,
                    Permission.READ_EXTERNAL_STORAGE
                ])
                backup_dir = os.path.join(primary_external_storage_path(), "Download", "ChamaBackups")
            else:
                backup_dir = os.path.join(os.getcwd(), "ChamaBackups")

            os.makedirs(backup_dir, exist_ok=True)
            backup_path = os.path.join(backup_dir, "family.db")

            # ✅ ensure db_path is a valid file path string
            if not isinstance(db_path, (str, bytes, os.PathLike)):
                raise TypeError(f"Expected file path, got {type(db_path).__name__}")

            source = sqlite3.connect(db_path)
            backup = sqlite3.connect(backup_path)
            source.backup(backup)
            backup.close()
            source.close()

            return f"✅ Local backup created successfully!\nLocation: {backup_path}"

        except Exception as e:
            return f"❌ Backup failed: {e}"

    def add_expenses(self, beneficially, expense_description, account_name, amount):
        time_value=CurrentTime().get_time()
        try:
            # Step 1: Get total available balance for the account
            self.cursor.execute("SELECT SUM(amount) FROM accounts WHERE accounttype=?", (account_name,))
            total_balance = self.cursor.fetchone()[0] or 0

            # Step 2: Get total expenses already recorded for that account
            self.cursor.execute("SELECT SUM(amount) FROM expenses WHERE accounttype=?", (account_name,))
            total_expenses = self.cursor.fetchone()[0] or 0

            # Step 3: Calculate remaining balance
            remaining_balance = total_balance - total_expenses

            # Step 4: Compare
            if remaining_balance >= int(amount):
                self.cursor.execute(
                    "INSERT INTO expenses (family_name, fullnames, accounttype, amount, paid_on) VALUES (?, ?, ?, ?,?)",
                    (beneficially, expense_description, account_name, amount,time_value)
                )
                self.conn.commit()
                return "Expense Added Successfully"
            else:
                return f"{account_name} Has Insufficient Funds"

        except Exception as e:
            return f"An error has occurred: {e}"

