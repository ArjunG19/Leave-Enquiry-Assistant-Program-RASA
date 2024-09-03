from typing import Any, Text, Dict, List
from datetime import datetime

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
import mysql.connector

class ActionCheckLeaveBalance(Action):

    def name(self) -> Text:
        return "action_check_leave_balance"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        print("balance")


        employee_id = tracker.get_slot('emp_id')
        leave_type = tracker.get_slot('leave_type')
        print(leave_type)

        if not employee_id:
            dispatcher.utter_message(text="Please provide your employee ID.")
            return []

        # Connect to your database and fetch leave balance
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            passwd="yourpasswd",
            database="leave_bot"
        )
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM leave_balance WHERE Emp_id=%s", (employee_id,))
        employee_exists = cursor.fetchone()[0] > 0

        if not employee_exists:
            dispatcher.utter_message(text="Employee ID not found.")
            conn.close()
            return []
        
        if leave_type:
            cursor.execute("SELECT lt.leave_type_name, lb.leave_balance FROM leave_balance lb JOIN leave_types lt ON lb.leave_type_id = lt.leave_type_id WHERE Emp_id=%s AND leave_type_name=%s", (employee_id, leave_type))
            result = cursor.fetchone()
            if result:
                print(leave_type)
                balance_message = f"Your {leave_type.lower()} leave balance is {result[1]} days."
            else:
                print(leave_type)
                balance_message = f"No balance information found for {leave_type.lower()}."

        else:
            cursor.execute("SELECT lt.leave_type_name,lb.leave_balance FROM leave_balance lb JOIN leave_types lt ON lb.leave_type_id = lt.leave_type_id WHERE lb.Emp_id =%s", (employee_id,))
            results = cursor.fetchall()
            if results:
                leave_balances = {row[0]: row[1] for row in results}
                balance_message = "Your leave balances are as follows:\n"
                for leave_type, balance in leave_balances.items():
                    balance_message += f"{leave_type.capitalize()}: {balance} days\n"
            else:
                balance_message = "No leave balance information available."

        dispatcher.utter_message(text=balance_message)

        return []

class ActionCheckLeavePolicy(Action):

    

    def name(self) -> Text:
        return "action_check_leave_policy"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        print("leave")

        employee_id = tracker.get_slot('emp_id')
        leave_type = tracker.get_slot('leave_type')

        if not employee_id:
            dispatcher.utter_message(text="Please provide your employee ID.")
            return []

        # Connect to your database and fetch leave balance
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            passwd="yourpasswd",
            database="leave_bot"
        )
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM leave_balance WHERE Emp_id=%s", (employee_id,))
        employee_exists = cursor.fetchone()[0] > 0

        if not employee_exists:
            dispatcher.utter_message(text="Employee ID not found.")
            conn.close()
            return []
        
        if leave_type:
            cursor.execute("SELECT lt.leave_type_name, lb.total_leave FROM leave_balance lb JOIN leave_types lt ON lb.leave_type_id = lt.leave_type_id WHERE Emp_id=%s AND leave_type_name=%s", (employee_id, leave_type))
            result = cursor.fetchone()
            if result:
                policy_message = f"You get {result[1]} days of total {leave_type.lower()} leaves."
            else:
                policy_message = f"No policy information found for {leave_type.lower()} leave."
        else:
            cursor.execute("SELECT lt.leave_type_name,lb.total_leave FROM leave_balance lb JOIN leave_types lt ON lb.leave_type_id = lt.leave_type_id WHERE lb.Emp_id =%s", (employee_id,))
            results = cursor.fetchall()
            if results:
                total_leaves = {row[0]: row[1] for row in results}
                policy_message = "Your leave policy is as follows:\n"
                for leave_type, total_leave in total_leaves.items():
                    policy_message += f"{leave_type.capitalize()}: {total_leave} days\n"
            else:
                policy_message = "No leave policy information available."

        dispatcher.utter_message(text=policy_message)
        
        conn.close()

        return []


