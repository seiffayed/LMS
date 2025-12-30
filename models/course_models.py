from datetime import datetime

class Course:
    def __init__(self, cid, title, instructor):
        self.cid = cid
        self.title = title
        self.instructor = instructor
        self.students = []
        self.materials = []
        self.assignments = []
        self.submissions = []
        self.announcements = []
        self.quizzes = []
        self.reviews = []

    def add_student(self, student):
        if student not in self.students:
            self.students.append(student)

    def has_submitted(self, student_username, assignment_title):
        for s in self.submissions:
            if s.student.get_username() == student_username and s.assignment.title == assignment_title:
                return True
        return False
