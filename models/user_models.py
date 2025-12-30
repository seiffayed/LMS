from abc import ABC, abstractmethod
from datetime import datetime
from utils import Validator

class PrivateMessage:
    def __init__(self, sender_name, subject, body):
        self.sender = sender_name
        self.subject = subject
        self.body = body
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        self.is_read = False
class CourseReview:
    def __init__(self, student_name, rating):
        self.student = student_name
        self.__rating = rating if 1 <= rating <= 5 else 5
        self.date = datetime.now().strftime("%Y-%m-%d")

class User(ABC):
    def __init__(self, username, password, email):
        self._username = username
        self.__password = password
        self._email = email
        self.notifications = []
        self.inbox = []


    def get_username(self): return self._username
    def get_email(self): return self._email
    def check_password(self, pwd): return self.__password == pwd

    def update_email(self, new_email):
        if Validator.validate_gmail(new_email):
            self._email = new_email
            return True
        return False

    def update_password(self, current_pwd, new_pwd):
        if self.check_password(current_pwd) and len(new_pwd) >= 6:
            self.__password = new_pwd
            return True
        return False

    def add_notification(self, message):
        self.notifications.append(f"[{datetime.now().strftime('%H:%M')}] {message}")

    def send_message(self, recipient_obj, subject, body):
        new_msg = PrivateMessage(self._username, subject, body)
        recipient_obj.inbox.append(new_msg)
        recipient_obj.add_notification(f"New message from {self._username}")

    def get_unread_count(self):
        return len([m for m in self.inbox if not m.is_read])



    @abstractmethod
    def get_role(self): pass

class Admin(User):
    def get_role(self): return "Admin"

class Instructor(User):
    def __init__(self, username, password, email):
        super().__init__(username, password, email)
        self.assigned_courses = []
    def get_role(self): return "Instructor"

class Student(User):
    def __init__(self, username, password, email):
        super().__init__(username, password, email)
        self.enrolled_courses = []
    def get_role(self): return "Student"
