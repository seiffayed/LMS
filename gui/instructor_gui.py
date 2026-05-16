import tkinter as tk
from tkinter import messagebox, ttk, filedialog
from datetime import datetime
from .base_window import BaseWindow
from color import MAROON, BROWN, GREEN, RED, FONT
from models.content_models import Assignment, LectureMaterial

class InstructorDashboard(BaseWindow):
    def __init__(self, user, lms):
        self.user, self.lms = user, lms
        self.win = tk.Tk()
        self.win.title(f"Instructor: {user.get_username()}")
        self.maximize_window(self.win)

        self.setup_ui()
        self.win.protocol("WM_DELETE_WINDOW", self.on_close)
        self.win.mainloop()

    def on_close(self):
        self.lms.save_to_file()
        self.win.destroy()

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

            tk.Button(f, text="View", command=read).pack(side="right")


    def setup_ui(self):
        sidebar = tk.Frame(self.win, bg=MAROON, width=220)
        sidebar.pack(side="left", fill="y")

        tk.Label(sidebar, text="Instructor", fg="white", bg=MAROON, font=("Arial", 16, "bold")).pack(pady=30)

        nav = [
            ("My Courses", self.show_courses),
            ("Students List", self.show_students),
            ("Grading Center", self.show_grading),
            ("Messages", self.show_inbox),

            ("Post Announcement", self.post_announcement_ui)
        ]

        for text, cmd in nav:
            tk.Button(sidebar, text=text, bg=BROWN, fg="white", font=FONT, command=cmd, relief="flat", bd=0).pack(fill="x", pady=2, padx=10)

        tk.Button(sidebar, text="LOGOUT", bg=RED, fg="white", command=self.logout).pack(side="bottom", fill="x", pady=20, padx=10)
        self.content = tk.Frame(self.win, bg="white", padx=30, pady=30)
        self.content.pack(side="right", fill="both", expand=True)
        self.show_courses()


    def post_announcement_ui(self):
        for w in self.content.winfo_children(): w.destroy()
        tk.Label(self.content, text="Broadcast Announcement", font=("Arial", 22, "bold"), bg="white").pack(anchor="w", pady=20)

        tk.Label(self.content, text="Select Course:", bg="white").pack(anchor="w")
        course_titles = [c.title for c in self.user.assigned_courses]
        course_cb = ttk.Combobox(self.content, values=course_titles, width=40)
        course_cb.pack(anchor="w", pady=5)

        tk.Label(self.content, text="Message Body:", bg="white").pack(anchor="w")
        msg_txt = tk.Text(self.content, height=8, width=60)
        msg_txt.pack(anchor="w", pady=5)

        def send():
            if not course_cb.get(): return messagebox.showerror("Error", "Select a course")
            target_course = next(c for c in self.user.assigned_courses if c.title == course_cb.get())
            announcement = f"[{datetime.now().strftime('%Y-%m-%d')}] {msg_txt.get('1.0', tk.END).strip()}"
            target_course.announcements.append(announcement)
            for s in target_course.students:
                s.add_notification(f"New Announcement in {target_course.title}")
            self.lms.log_event(f"Announcement posted to {target_course.title}")
            self.lms.save_to_file()
            messagebox.showinfo("Sent", "Notification broadcasted to all students.")
            msg_txt.delete("1.0", tk.END)

        tk.Button(self.content, text="POST TO CLASSROOM", bg=GREEN, fg="white", font=FONT, command=send).pack(pady=20, anchor="w")

    def show_courses(self):
        for w in self.content.winfo_children(): w.destroy()
        tk.Label(self.content, text="Managed Courses", font=("Arial", 22, "bold"), bg="white").pack(anchor="w")
        for c in self.user.assigned_courses:
            if not hasattr(c, 'quizzes'): c.quizzes = []
            f = tk.Frame(self.content, bg="#f9f9f9", pady=10, padx=10, relief="groove", bd=1)
            f.pack(fill="x", pady=5)
            tk.Label(f, text=c.title, font=FONT, bg="#f9f9f9").pack(side="left")

            tk.Button(f, text="+ Assignment", bg=BROWN, fg="white", command=lambda c=c: self.add_assignment_ui(c)).pack(side="right", padx=5)
            tk.Button(f, text="+ Material", bg=GREEN, fg="white", command=lambda c=c: self.add_material_ui(c)).pack(side="right", padx=5)
    def show_grading(self):
        for w in self.content.winfo_children(): w.destroy()
        tk.Label(self.content, text="Grading Center (Pending Work)", font=("Arial", 22, "bold"), bg="white").pack(anchor="w", pady=(0,20))

        found_any = False
        for c in self.user.assigned_courses:
            for sub in c.submissions:
                if sub.is_graded:
                    continue

                found_any = True
                row = tk.Frame(self.content, bg="#eee", pady=10, padx=10)
                row.pack(fill="x", pady=5)
                info = f"Student: {sub.student.get_username()} | Task: {sub.assignment.title}"
                tk.Label(row, text=info, bg="#eee", font=FONT).pack(side="left")

                tk.Button(row, text="Evaluate", bg=BROWN, fg="white", command=lambda s=sub: self.grade_popup(s)).pack(side="right")

        if not found_any:
            tk.Label(self.content, text="All caught up! No submissions pending.", fg="gray", bg="white", font=FONT).pack(pady=50)
    def grade_popup(self, sub):
        pop = tk.Toplevel(self.win)
        pop.title("Grade Work")
        self.center_window(pop, 400, 500)
        tk.Label(pop, text="Student Response:", font=FONT).pack(pady=10)
        txt = tk.Text(pop, height=10, width=45)
        txt.insert("1.0", sub.content)
        txt.config(state="disabled")
        txt.pack(pady=10)
        tk.Label(pop, text=f"Grade (Max {sub.assignment.max_marks}):").pack()
        grade_ent = tk.Entry(pop)
        grade_ent.pack()

        def submit_grade():
            try:
                score = int(grade_ent.get())
                if score > sub.assignment.max_marks:
                    return messagebox.showerror("Invalid Grade",
                        f"Score ({score}) cannot exceed maximum marks ({sub.assignment.max_marks})!")

                if score < 0:
                    return messagebox.showerror("Invalid Grade", "Score cannot be negative!")
                sub.assignment.set_grade(sub.student.get_username(), score)
                sub.is_graded = True
                sub.student.add_notification(f"Graded: {sub.assignment.title} -> {score}/{sub.assignment.max_marks}")
                self.lms.save_to_file()
                messagebox.showinfo("Done", f"Grade of {score} assigned successfully.")
                pop.destroy()
                self.show_grading()

            except ValueError:
                messagebox.showerror("Error", "Please enter a valid whole number for the grade.")

        tk.Button(pop, text="Save Grade", bg=GREEN, fg="white", command=submit_grade).pack(pady=20)

    def add_material_ui(self, course):
        pop = tk.Toplevel(self.win)
        pop.title(f"New Material: {course.title}")
        self.center_window(pop, 500, 600)
        pop.configure(bg="white")
        tk.Label(pop, text="Upload Study Material", font=("Arial", 16, "bold"), bg="white", fg=MAROON).pack(pady=20)
        tk.Label(pop, text="Material Title:", bg="white").pack(anchor="w", padx=50)
        t_ent = tk.Entry(pop, width=40, font=("Arial", 11)); t_ent.pack(pady=5)
        tk.Label(pop, text="Content Description:", bg="white").pack(anchor="w", padx=50)
        d_txt = tk.Text(pop, height=6, width=40, font=("Arial", 10)); d_txt.pack(pady=5)
        path_label = tk.Label(pop, text="No PDF/File Attached", fg="gray", bg="white")
        path_label.pack(pady=10)

        def browse_file():
            file = filedialog.askopenfilename(title="Select Material File",
                                            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")])
            if file: path_label.config(text=file, fg=GREEN)
        tk.Button(pop, text="BROWSE FILES", command=browse_file, width=20).pack()

        def save_material():
            if not t_ent.get(): return messagebox.showerror("Error", "Title is mandatory!")
            new_mat = LectureMaterial(t_ent.get(), d_txt.get("1.0", tk.END), path_label.cget("text"))
            course.materials.append(new_mat)

            for student in course.students:
                student.add_notification(f"New Material in {course.title}: {new_mat.title}")

            self.lms.save_to_file()
            messagebox.showinfo("Success", "Course Material has been published!")
            pop.destroy()
            self.show_courses()

        tk.Button(pop, text="PUBLISH MATERIAL", bg=GREEN, fg="white",
                  font=FONT, command=save_material).pack(pady=30, ipady=5, fill="x", padx=50)

    def add_assignment_ui(self, course):
        pop = tk.Toplevel(self.win)
        pop.title("Create New Assignment")
        self.center_window(pop, 500, 650)
        tk.Label(pop, text="New Assessment", font=("Arial", 16, "bold")).pack(pady=20)
        fields = [("Title:", "Homework"), ("Deadline (YYYY-MM-DD):", "2024-12-31"), ("Max Grade:", "100")]
        entries = {}

        for lbl, default in fields:
            tk.Label(pop, text=lbl).pack(anchor="w", padx=50)
            e = tk.Entry(pop, width=40)
            e.insert(0, default)
            e.pack(pady=5)
            entries[lbl] = e

        tk.Label(pop, text="Assignment Instructions:").pack(anchor="w", padx=50)
        instr = tk.Text(pop, height=5, width=40)
        instr.pack(pady=5)

        def save_task():
            try:
                title = entries["Title:"].get()
                date = entries["Deadline (YYYY-MM-DD):"].get()
                marks = int(entries["Max Grade:"].get())
                new_a = Assignment(title, instr.get("1.0", tk.END), date, marks)
                course.assignments.append(new_a)

                for s in course.students:
                    s.add_notification(f"New Assignment: {title} (Due {date})")
                
                self.lms.save_to_file()
                messagebox.showinfo("Created", "Assignment is now visible to students.")
                pop.destroy()
            except:
                messagebox.showerror("Error", "Invalid Marks Value")

        tk.Button(pop, text="CREATE TASK", bg=BROWN, fg="white", font=FONT,
                  command=save_task).pack(pady=20, fill="x", padx=50)



    def show_students(self):
        for w in self.content.winfo_children(): w.destroy()
        tk.Label(self.content, text="Student Management & Reporting", font=("Arial", 22, "bold"), bg="white").pack(anchor="w", pady=20)

        if not self.user.assigned_courses:
            tk.Label(self.content, text="You have no courses assigned.", bg="white").pack()
            return

        for c in self.user.assigned_courses:
            tk.Label(self.content, text=f"COURSE: {c.title}", font=FONT, fg=BROWN, bg="white").pack(anchor="w", pady=(10,0))

            if not c.students:
                tk.Label(self.content, text="   (No students enrolled)", fg="gray", bg="white").pack(anchor="w")

            for s in c.students:
                row = tk.Frame(self.content, bg="white", pady=5)
                row.pack(fill="x", padx=20)
                tk.Label(row, text=f"• {s.get_username()}", bg="white", width=20, anchor="w").pack(side="left")

                tk.Button(row, text="View Detailed Report", font=("Segoe UI", 9),
                          command=lambda stud=s, crs=c: self.generate_individual_report(stud, crs)).pack(side="left", padx=10)

    def generate_individual_report(self, student, course):
        report_win = tk.Toplevel(self.win)
        report_win.title(f"Report: {student.get_username()}")
        self.center_window(report_win, 550, 700)

        tk.Label(report_win, text=f"Academic Record: {student.get_username()}", font=("Arial", 16, "bold")).pack(pady=20)
        tk.Label(report_win, text=f"Course: {course.title}", font=FONT).pack()

        info_box = tk.Text(report_win, height=25, width=60, font=("Consolas", 10), padx=10, pady=10)
        info_box.pack(pady=20, padx=20)
        report_data = f"OFFICIAL ACADEMIC REPORT\n"
        report_data += f"GENERATED ON: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
        report_data += "-"*50 + "\n\n"

        report_data += "--- ASSIGNMENT PROGRESS ---\n"
        total_score = 0
        count = 0
        for a in course.assignments:
            grade = a.get_grade(student.get_username())
            report_data += f" - {a.title:<25}: {grade}\n"
            if isinstance(grade, (int, float)):
                total_score += grade
                count += 1

        report_data += "\n--- QUIZ PERFORMANCE ---\n"
        if not hasattr(course, 'quizzes') or not course.quizzes:
            report_data += " No quizzes available in this course.\n"
        else:
            for q in course.quizzes:
                score = q.get_score(student.get_username())
                report_data += f" - {q.title:<25}: {score}\n"

        report_data += "\n" + "-"*50 + "\n"
        avg = (total_score / count) if count > 0 else 0
        report_data += f"CURRENT ASSIGNMENT AVG: {avg:.2f}%\n"

        submissions_count = len([s for s in course.submissions if s.student == student])
        report_data += f"TOTAL TASKS SUBMITTED: {submissions_count}\n"

        info_box.insert(tk.END, report_data)
        info_box.config(state="disabled")

        tk.Button(report_win, text="Close Report", command=report_win.destroy, bg=RED, fg="white", font=FONT).pack(pady=10)
    def logout(self):
        self.win.destroy()
        from .auth_gui import LoginGUI
        LoginGUI(self.lms)
