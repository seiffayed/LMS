import sqlite3
import json
from .user_models import Admin, Instructor, Student, PrivateMessage
from .course_models import Course
from .content_models import Assignment, LectureMaterial, Submission

class DatabaseManager:
    DB_NAME = "lms_data.db"

    def __init__(self):
        self.conn = None
        self.create_tables()

    def connect(self):
        self.conn = sqlite3.connect(self.DB_NAME)
        self.conn.row_factory = sqlite3.Row

    def close(self):
        if self.conn:
            self.conn.close()

    def create_tables(self):
        self.connect()
        cursor = self.conn.cursor()
        
        # Enable foreign keys
        cursor.execute("PRAGMA foreign_keys = ON;")

        # Users
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                password TEXT,
                email TEXT,
                role TEXT
            )
        """)

        # Courses
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS courses (
                cid TEXT PRIMARY KEY,
                title TEXT,
                instructor_username TEXT,
                FOREIGN KEY(instructor_username) REFERENCES users(username)
            )
        """)

        # Enrollments
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS enrollments (
                student_username TEXT,
                course_cid TEXT,
                FOREIGN KEY(student_username) REFERENCES users(username),
                FOREIGN KEY(course_cid) REFERENCES courses(cid)
            )
        """)

        # Assignments
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS assignments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                course_cid TEXT,
                title TEXT,
                description TEXT,
                deadline TEXT,
                max_marks INTEGER,
                FOREIGN KEY(course_cid) REFERENCES courses(cid)
            )
        """)

        # Assignment Grades
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS assignment_grades (
                assignment_id INTEGER,
                student_username TEXT,
                score INTEGER,
                FOREIGN KEY(assignment_id) REFERENCES assignments(id),
                FOREIGN KEY(student_username) REFERENCES users(username)
            )
        """)

        # Materials
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS materials (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                course_cid TEXT,
                title TEXT,
                description TEXT,
                file_path TEXT,
                FOREIGN KEY(course_cid) REFERENCES courses(cid)
            )
        """)



        # Submissions
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS submissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                course_cid TEXT,
                assignment_title TEXT,
                student_username TEXT,
                content TEXT,
                date TEXT,
                is_graded INTEGER,
                FOREIGN KEY(course_cid) REFERENCES courses(cid),
                FOREIGN KEY(student_username) REFERENCES users(username)
            )
        """)



        # Messages
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sender TEXT,
                recipient TEXT,
                subject TEXT,
                body TEXT,
                timestamp TEXT,
                is_read INTEGER,
                FOREIGN KEY(recipient) REFERENCES users(username)
            )
        """)

        # Notifications
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT,
                message TEXT,
                FOREIGN KEY(username) REFERENCES users(username)
            )
        """)

        # Logs
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message TEXT
            )
        """)

        # Announcements
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS announcements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                course_cid TEXT,
                message TEXT,
                FOREIGN KEY(course_cid) REFERENCES courses(cid)
            )
        """)

        self.conn.commit()
        self.close()

    def save_full_state(self, users, courses, logs):
        self.connect()
        cursor = self.conn.cursor()
        
        # Clear all tables
        tables = ["users", "courses", "enrollments", "assignments", "assignment_grades",
                  "materials", "quizzes", "quiz_attempts", "submissions", "messages", 
                  "notifications", "logs", "announcements"]
        for t in tables:
            cursor.execute(f"DELETE FROM {t}")
        
        # Save Users
        for u in users:
            role = u.get_role()
            cursor.execute("INSERT INTO users (username, password, email, role) VALUES (?, ?, ?, ?)",
                           (u.get_username(), u._User__password, u.get_email(), role))
            
            # Save Notifications
            for n in u.notifications:
                cursor.execute("INSERT INTO notifications (username, message) VALUES (?, ?)", (u.get_username(), n))
            


            # Save Inbox
            for m in u.inbox:
                cursor.execute("""
                    INSERT INTO messages (sender, recipient, subject, body, timestamp, is_read) 
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (m.sender, u.get_username(), m.subject, m.body, m.timestamp, 1 if m.is_read else 0))

        # Save Courses
        for c in courses:
            cursor.execute("INSERT INTO courses (cid, title, instructor_username) VALUES (?, ?, ?)",
                           (c.cid, c.title, c.instructor.get_username()))
            
            # Enrollments
            for s in c.students:
                cursor.execute("INSERT INTO enrollments (student_username, course_cid) VALUES (?, ?)",
                               (s.get_username(), c.cid))
            
            # Announcements
            for a in c.announcements:
                 cursor.execute("INSERT INTO announcements (course_cid, message) VALUES (?, ?)", (c.cid, a))
            
            # Assignments
            for a in c.assignments:
                cursor.execute("""
                    INSERT INTO assignments (course_cid, title, description, deadline, max_marks) 
                    VALUES (?, ?, ?, ?, ?)
                """, (c.cid, a.title, a.description, a.deadline, a.max_marks))
                params_id = cursor.lastrowid
                
                # Grades
                for stud_user, score in a._Assignment__grades.items():
                     cursor.execute("INSERT INTO assignment_grades (assignment_id, student_username, score) VALUES (?, ?, ?)",
                                    (params_id, stud_user, score))
            
            # Materials
            for m in c.materials:
                cursor.execute("""
                    INSERT INTO materials (course_cid, title, description, file_path) 
                    VALUES (?, ?, ?, ?)
                """, (c.cid, m.title, m.description, m.file_path))
                

                                   
            # Submissions 
            for sub in c.submissions:
                 cursor.execute("""
                    INSERT INTO submissions (course_cid, assignment_title, student_username, content, date, is_graded)
                    VALUES (?, ?, ?, ?, ?, ?)
                 """, (c.cid, sub.assignment.title, sub.student.get_username(), sub.content, sub.date, 1 if sub.is_graded else 0))

        # Save Logs
        for l in logs:
            cursor.execute("INSERT INTO logs (message) VALUES (?)", (l,))

        self.conn.commit()
        self.close()

    def load_full_state(self):
        self.connect()
        cursor = self.conn.cursor()
        
        users_map = {} # username -> object
        courses = []
        logs = []

        # Load Users
        cursor.execute("SELECT * FROM users")
        for row in cursor.fetchall():
            u = None
            if row['role'] == 'Admin':
                u = Admin(row['username'], row['password'], row['email'])
            elif row['role'] == 'Instructor':
                u = Instructor(row['username'], row['password'], row['email'])
            elif row['role'] == 'Student':
                u = Student(row['username'], row['password'], row['email'])
            
            users_map[row['username']] = u
            
            # Load Notifications
            cursor.execute("SELECT message FROM notifications WHERE username = ?", (row['username'],))
            u.notifications = [r['message'] for r in cursor.fetchall()]
            


            # Load Inbox
            cursor.execute("SELECT * FROM messages WHERE recipient = ?", (row['username'],))
            for m_row in cursor.fetchall():
                msg = PrivateMessage(m_row['sender'], m_row['subject'], m_row['body'])
                msg.timestamp = m_row['timestamp']
                msg.is_read = bool(m_row['is_read'])
                u.inbox.append(msg)

        # Load Courses
        cursor.execute("SELECT * FROM courses")
        for c_row in cursor.fetchall():
            inst = users_map.get(c_row['instructor_username'])
            course = Course(c_row['cid'], c_row['title'], inst)
            if inst and isinstance(inst, Instructor):
                inst.assigned_courses.append(course)
            
            courses.append(course)
            
            # Enrollments
            cursor.execute("SELECT student_username FROM enrollments WHERE course_cid = ?", (c_row['cid'],))
            for e_row in cursor.fetchall():
                s = users_map.get(e_row['student_username'])
                if s and isinstance(s, Student):
                    course.add_student(s)
                    s.enrolled_courses.append(course)
            
            # Announcements
            cursor.execute("SELECT message FROM announcements WHERE course_cid = ?", (c_row['cid'],))
            course.announcements = [r['message'] for r in cursor.fetchall()]

            # Materials
            cursor.execute("SELECT * FROM materials WHERE course_cid = ?", (c_row['cid'],))
            for m_row in cursor.fetchall():
                course.materials.append(LectureMaterial(m_row['title'], m_row['description'], m_row['file_path']))

            # Assignments
            cursor.execute("SELECT * FROM assignments WHERE course_cid = ?", (c_row['cid'],))
            for a_row in cursor.fetchall():
                assign = Assignment(a_row['title'], a_row['description'], a_row['deadline'], a_row['max_marks'])
                # Grades
                cursor.execute("SELECT * FROM assignment_grades WHERE assignment_id = ?", (a_row['id'],))
                for g_row in cursor.fetchall():
                    assign.set_grade(g_row['student_username'], g_row['score'])
                course.assignments.append(assign)


            
            # Submissions
            cursor.execute("SELECT * FROM submissions WHERE course_cid = ?", (c_row['cid'],))
            for s_row in cursor.fetchall():
                student_obj = users_map.get(s_row['student_username'])
                # Need to find assignment object reference
                assign_obj = next((a for a in course.assignments if a.title == s_row['assignment_title']), None)
                
                if student_obj and assign_obj:
                    sub = Submission(student_obj, course, assign_obj, s_row['content'])
                    sub.date = s_row['date']
                    sub.is_graded = bool(s_row['is_graded'])
                    course.submissions.append(sub)

        # Load Logs
        cursor.execute("SELECT message FROM logs")
        logs = [r['message'] for r in cursor.fetchall()]

        self.close()
        return list(users_map.values()), courses, logs
