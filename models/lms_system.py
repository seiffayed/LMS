from datetime import datetime
from .database_manager import DatabaseManager
from .user_models import Admin, Instructor, Student
from .course_models import Course
from .content_models import Assignment

class LMS:
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.users = []
        self.courses = []
        self.logs = []
        
        self.load_from_db()
        
        if not self.users:
             self.users = [
                Admin("admin", "admin123", "admin@gmail.com"),
                Instructor("pro", "pro123", "pro@gmail.com"),
                Student("student", "stud123", "student@gmail.com")
             ]
             self._init_data()
             self.save_to_file()

    def save_to_file(self):
        self.db_manager.save_full_state(self.users, self.courses, self.logs)
        print("System Data Auto-Saved to SQLite.")

    def load_from_db(self):
        try:
            self.users, self.courses, self.logs = self.db_manager.load_full_state()
            if self.users:
                self.log_event("Restored system state from database.")
        except Exception as e:
            print(f"Error loading database: {e}")

    def _init_data(self):
        c1 = Course("CS101", "Advanced Python", self.users[1])
        c1.assignments.append(Assignment("Final Project", "Build an LMS", "2025-01-01", 100))
        self.courses.append(c1)
        self.users[1].assigned_courses.append(c1)
        self.log_event("System Secure Boot: Initialized.")

    def log_event(self, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.logs.append(f"{timestamp} | EVENT: {message}")

    def register_user(self, username, password, email, role):
        if any(u.get_username() == username for u in self.users):
            return False, "User exists."
        new_user = Student(username, password, email) if role == "Student" else Instructor(username, password, email)
        self.users.append(new_user)
        self.log_event(f"New {role} registered: {username}")
        return True, "Success"

    def authenticate(self, username, password):
        for u in self.users:
            if u.get_username() == username and u.check_password(password):
                self.log_event(f"Secure Login: {username}")
                return u
        return None
