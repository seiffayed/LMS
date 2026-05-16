import tkinter as tk
from tkinter import messagebox, ttk
import os
from .base_window import BaseWindow
from color import MAROON, BROWN, GREEN, RED, FONT
from models.user_models import CourseReview
from models.content_models import Submission

class StudentDashboard(BaseWindow):
    def __init__(self, user, lms):
        self.user, self.lms = user, lms
        self.win = tk.Tk()
        self.win.title(f"Learner: {user.get_username()}")
        self.maximize_window(self.win)
        self.setup_ui()
        self.win.protocol("WM_DELETE_WINDOW", self.on_close)
        self.win.mainloop()

    def on_close(self):
        self.lms.save_to_file()
        self.win.destroy()



    def leave_feedback_ui(self, course):
        pop = tk.Toplevel(self.win)
        pop.title(f"Review: {course.title}")
        self.center_window(pop, 400, 350)

        tk.Label(pop, text="Rate this Course (1 to 5):", font=FONT).pack(pady=10)
        score_var = tk.IntVar(value=5)
        tk.Scale(pop, from_=1, to=5, orient="horizontal", variable=score_var).pack()

        tk.Label(pop, text="Your Comments:", font=FONT).pack(pady=10)

        def save_review():
            new_review = CourseReview(self.user.get_username(), score_var.get())
            course.reviews.append(new_review)
            self.lms.save_to_file()
            messagebox.showinfo("Feedback Sent", "Thank you for helping us improve!")
            pop.destroy()

        tk.Button(pop, text="SUBMIT REVIEW", bg=GREEN, fg="white", command=save_review).pack(pady=15)

    def show_inbox(self):
        target = self.content if hasattr(self, 'content') else self.main
        for w in target.winfo_children(): w.destroy()
        tk.Label(target, text="Private Inbox", font=("Arial", 22, "bold"), bg="white").pack(anchor="w", pady=20)
        bar = tk.Frame(target, bg="white")
        bar.pack(fill="x", pady=10)

        def compose():
            pop = tk.Toplevel(self.win)
            pop.title("New Message")
            self.center_window(pop, 400, 450)
            tk.Label(pop, text="Recipient Username:").pack(pady=5)
            rec_ent = tk.Entry(pop); rec_ent.pack(pady=5)
            tk.Label(pop, text="Subject:").pack(pady=5)
            sub_ent = tk.Entry(pop); sub_ent.pack(pady=5)
            tk.Label(pop, text="Message Body:").pack(pady=5)
            body_txt = tk.Text(pop, height=8, width=35); body_txt.pack(pady=5)

            def send():
                recipient = next((u for u in self.lms.users if u.get_username() == rec_ent.get()), None)
                if recipient:
                    self.user.send_message(recipient, sub_ent.get(), body_txt.get("1.0", tk.END))
                    messagebox.showinfo("Sent", "Message delivered!")
                    pop.destroy()
                    self.show_inbox()
                else:
                    messagebox.showerror("Error", "User not found.")

            tk.Button(pop, text="Send Now", bg=GREEN, fg="white", command=send).pack(pady=10)

        tk.Button(bar, text="+ Compose New", bg=BROWN, fg="white", command=compose).pack(side="right")

        if not self.user.inbox:
            tk.Label(target, text="No messages yet.", fg="gray", bg="white").pack(pady=50)
            return

        for msg in reversed(self.user.inbox):
            color = "#f4f4f4" if msg.is_read else "#fff9db"
            f = tk.Frame(target, bg=color, pady=10, padx=15, relief="solid", bd=1)
            f.pack(fill="x", pady=5)
            lbl = f"From: {msg.sender} | {msg.subject} ({msg.timestamp})"
            tk.Label(f, text=lbl, bg=color, font=("Segoe UI", 10, "bold" if not msg.is_read else "normal")).pack(side="left")

            def read(m=msg):
                m.is_read = True
                messagebox.showinfo(m.subject, f"From: {m.sender}\nDate: {m.timestamp}\n\n{m.body}")
                self.show_inbox()

            tk.Button(f, text="View", bg=BROWN, fg="white", command=read).pack(side="right")


    def setup_ui(self):
        sidebar = tk.Frame(self.win, bg=BROWN, width=220)
        sidebar.pack(side="left", fill="y")

        tk.Label(sidebar, text="LEARNER", fg="white", bg=BROWN, font=("Arial", 16, "bold")).pack(pady=30)
        tk.Button(sidebar, text="Enroll Classroom", bg=BROWN, fg="white", font=FONT, command=self.show_catalog).pack(fill="x", pady=2, padx=10)
        tk.Button(sidebar, text="My Classroom", bg=BROWN, fg="white", font=FONT, command=self.show_my_courses).pack(fill="x", pady=2, padx=10)
        tk.Button(sidebar, text="Messages", bg=BROWN, fg="white", font=FONT, command=self.show_inbox).pack(fill="x", pady=2, padx=10)


        tk.Label(sidebar, text="Notifications", fg="white", bg=BROWN, font=FONT).pack(pady=(30, 0))
        self.note_box = tk.Listbox(sidebar, height=10, font=("Arial", 8))
        self.note_box.pack(padx=10, pady=5)
        for n in self.user.notifications: self.note_box.insert(tk.END, n)
        tk.Button(sidebar, text="LOGOUT", bg=RED, fg="white", command=self.logout).pack(side="bottom", fill="x", pady=20, padx=10)
        self.main = tk.Frame(self.win, bg="#f5f5f5", padx=30, pady=30)
        self.main.pack(side="right", fill="both", expand=True)
        self.show_my_courses()

    def show_catalog(self):
        for w in self.main.winfo_children(): w.destroy()
        tk.Label(self.main, text="Available Courses", font=("Arial", 22, "bold"), bg="#f5f5f5").pack(anchor="w")

        for c in self.lms.courses:
            if c not in self.user.enrolled_courses:
                row = tk.Frame(self.main, bg="white", pady=10, padx=15)
                row.pack(fill="x", pady=5)
                tk.Label(row, text=f"{c.title} (By {c.instructor.get_username()})", font=FONT, bg="white").pack(side="left")
                tk.Button(row, text="Enroll", bg=GREEN, fg="white", command=lambda c=c: self.enroll(c)).pack(side="right")

    def enroll(self, course):
        self.user.enrolled_courses.append(course)
        course.add_student(self.user)
        self.lms.save_to_file()
        messagebox.showinfo("Success", f"Enrolled in {course.title}")
        self.show_my_courses()

    def show_my_courses(self):
        for w in self.main.winfo_children(): w.destroy()
        tk.Label(self.main, text="My Classroom", font=("Arial", 22, "bold"), bg="#f5f5f5").pack(anchor="w", pady=(0,20))

        if not self.user.enrolled_courses:
            tk.Label(self.main, text="You are not enrolled in any courses.", bg="#f5f5f5").pack(pady=20)

        for c in self.user.enrolled_courses:
            card = tk.Frame(self.main, bg="white", pady=15, padx=15, bd=1, relief="solid")
            card.pack(fill="x", pady=10)
            tk.Label(card, text=c.title, font=FONT, bg="white").pack(side="left")
            tk.Button(card, text="Enter Classroom", bg=BROWN, fg="white", command=lambda c=c: self.open_course(c)).pack(side="right")

    def open_course(self, course):
        top = tk.Toplevel(self.win)
        top.title(f"Classroom: {course.title}")
        self.center_window(top, 850, 650)
        nb = ttk.Notebook(top)
        nb.pack(fill="both", expand=True, padx=10, pady=10)
        tk.Button(top, text="Leave Course Feedback", bg=BROWN, fg="white", command=lambda: self.leave_feedback_ui(course)).pack(pady=5)

        # TAB 1: Notice Board
        tab_news = tk.Frame(nb, bg="white")
        nb.add(tab_news, text="Notice Board")
        if not course.announcements:
            tk.Label(tab_news, text="No announcements yet.", bg="white", fg="gray").pack(pady=50)
        else:
            for ann in reversed(course.announcements):
                tk.Label(tab_news, text=ann, bg="#fffbe6", pady=10, padx=10, relief="solid", bd=1, wraplength=700, justify="left").pack(fill="x", pady=5, padx=20)

        # TAB 2: Materials
        tab_materials = tk.Frame(nb, bg="white")
        nb.add(tab_materials, text="Materials")

        if not course.materials:
            tk.Label(tab_materials, text="No study materials uploaded.", bg="white").pack(pady=20)

        for mat in course.materials:
            m_f = tk.Frame(tab_materials, bg="#f9f9f9", pady=10, padx=10, relief="groove", bd=1)
            m_f.pack(fill="x", pady=5, padx=10)

            info_frame = tk.Frame(m_f, bg="#f9f9f9")
            info_frame.pack(side="left", fill="both", expand=True)

            tk.Label(info_frame, text=mat.title, font=("Segoe UI", 12, "bold"), bg="#f9f9f9").pack(anchor="w")
            tk.Label(info_frame, text=mat.description, bg="#f9f9f9", fg="#555").pack(anchor="w")

            tk.Button(m_f, text="VIEW PDF / FILE", bg=MAROON, fg="white", font=("Segoe UI", 9, "bold"),
                      command=lambda p=mat.file_path: self.view_file(p)).pack(side="right", padx=10)

        # TAB 3: Assignments
        tab_tasks = tk.Frame(nb, bg="white")
        nb.add(tab_tasks, text="Assignments")
        for ass in course.assignments:
            a_f = tk.Frame(tab_tasks, bg="white", pady=10, padx=10, relief="solid", bd=1)
            a_f.pack(fill="x", pady=5, padx=10)
            tk.Label(a_f, text=f"{ass.title} (Max: {ass.max_marks})", font=FONT, bg="white").pack(side="left")

            if course.has_submitted(self.user.get_username(), ass.title):
                grade = ass.get_grade(self.user.get_username())
                tk.Label(a_f, text=f"Submitted - Grade: {grade}", fg=BROWN, bg="white").pack(side="right")
            else:
                tk.Button(a_f, text="Submit", bg=GREEN, fg="white", command=lambda a=ass, c=course: self.submit_ui(a, c, top)).pack(side="right")

        # TAB 4: Quizzat

    def view_file(self, path):
        if not path or path == "No PDF/File Attached":
            messagebox.showerror("Error", "No file was attached to this material.")
            return

        if os.path.exists(path):
            try:
                os.startfile(path)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open file: {e}")
        else:
            messagebox.showerror("File Error", f"The file at {path} could not be found.\n\nIt may have been moved or deleted.")

    def submit_ui(self, ass, course, top_win):
        pop = tk.Toplevel(self.win)
        pop.title("Upload Work")
        self.center_window(pop, 450, 400)
        tk.Label(pop, text=f"Submit: {ass.title}", font=("Arial", 12, "bold")).pack(pady=10)
        entry = tk.Text(pop, height=10, width=50)
        entry.pack(pady=10, padx=20)

        def confirm():
            new_sub = Submission(self.user, course, ass, entry.get("1.0", tk.END))
            course.submissions.append(new_sub)
            self.lms.save_to_file()
            messagebox.showinfo("Success", "Work Submitted!")
            pop.destroy()
            top_win.destroy()

        tk.Button(pop, text="SUBMIT WORK", bg=GREEN, fg="white", command=confirm).pack(pady=10)



    def logout(self):
        self.win.destroy()
        from .auth_gui import LoginGUI
        LoginGUI(self.lms)
