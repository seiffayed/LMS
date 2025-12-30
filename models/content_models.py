from datetime import datetime
from .abc_models import BaseContent

class LectureMaterial(BaseContent):
    def __init__(self, title, description, file_path):
        super().__init__(title, description)
        self.file_path = file_path

    def get_info(self):
        return f"Material: {self.title} (File: {self.file_path})"

class Assignment(BaseContent):
    def __init__(self, title, description, deadline, max_marks):
        super().__init__(title, description)
        self.deadline = deadline
        self.max_marks = max_marks
        self.__grades = {}

    def get_info(self):
        return f"Assignment: {self.title} (Due: {self.deadline})"

    def set_grade(self, student_user, score):
        self.__grades[student_user] = score

    def get_grade(self, student_user):
        return self.__grades.get(student_user, "Pending")

class Submission:
    def __init__(self, student_obj, course_obj, assignment_obj, content):
        self.student = student_obj
        self.course = course_obj
        self.assignment = assignment_obj
        self.content = content
        self.date = datetime.now().strftime("%Y-%m-%d %H:%M")
        self.is_graded = False
