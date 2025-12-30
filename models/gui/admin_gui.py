import tkinter as tk
from tkinter import messagebox, ttk, simpledialog
from .base_window import BaseWindow
from color import MAROON, BROWN, GREEN, RED, FONT
from models.course_models import Course
from models.report_models import UserReport, CourseReport


class AdminDashboard(BaseWindow):
    def __init__(self, user, lms):
        self.user, self.lms = user, lms
        self.win = tk.Tk()
        self.win = tk.Tk()
        self.win.title("Admin Only")
        self.maximize_window(self.win)
        self.setup_ui()
        self.win.protocol("WM_DELETE_WINDOW", self.on_close)
        self.win.mainloop()

    def on_close(self):
        self.lms.save_to_file()
        self.win.destroy()

    def setup_ui(self):
        side = tk.Frame(self.win, bg=MAROON, width=240)
        side.pack(side="left", fill="y")
        tk.Label(side, text="Admin", fg="white", bg=MAROON, font=("Arial", 18, "bold")).pack(pady=40)

        menu = [
            ("System Overview", self.show_overview),
            ("Manage Users", self.show_users),
            ("Manage Courses", self.show_courses),
            ("Security Logs", self.show_logs),
            ("Course Statistics", self.show_stats),
            ("Reports Center", self.show_reports_center)
        ]

        for text, cmd in menu:
            tk.Button(side, text=text, bg=BROWN, fg="white", font=FONT, bd=0, command=cmd).pack(fill="x", pady=2, padx=10, ipady=5)

        tk.Button(side, text="LOGOUT", bg=RED, fg="white", font=FONT, command=self.logout).pack(side="bottom", fill="x", pady=30, padx=10)
        self.main_work = tk.Frame(self.win, bg="#ecf0f1", padx=40, pady=40)
        self.main_work.pack(side="right", fill="both", expand=True)
        self.show_overview()

    def show_overview(self):
        for w in self.main_work.winfo_children(): w.destroy()
        tk.Label(self.main_work, text="System Statistics", font=("Arial", 26, "bold"), bg="#ecf0f1").pack(anchor="w")

        stats_f = tk.Frame(self.main_work, bg="#ecf0f1")
        stats_f.pack(fill="x", pady=30)

        data = [
            ("Total Users", len(self.lms.users)),
            ("Active Courses", len(self.lms.courses)),
            ("Students", len([u for u in self.lms.users if u.get_role()=="Student"]))
        ]
        for label, val in data:
            box = tk.Frame(stats_f, bg="white", width=200, height=120, relief="flat", padx=20, pady=20)
            box.pack_propagate(False)
            box.pack(side="left", padx=15)
            tk.Label(box, text=val, font=("Arial", 24, "bold"), bg="white", fg=MAROON).pack()
            tk.Label(box, text=label, font=("Arial", 12), bg="white").pack()

    def show_users(self):
        for w in self.main_work.winfo_children(): w.destroy()
        tk.Label(self.main_work, text="User Management", font=("Arial", 22, "bold"), bg="#ecf0f1").pack(anchor="w", pady=(0,20))

        for u in self.lms.users:
            row = tk.Frame(self.main_work, bg="white", pady=10, padx=10)
            row.pack(fill="x", pady=2)
            tk.Label(row, text=f"{u.get_username()} ({u.get_role()}) - {u.get_email()}", bg="white").pack(side="left")
            if u.get_role() != "Admin":
                tk.Button(row, text="Remove", bg=RED, fg="white", command=lambda x=u: self.delete_user(x)).pack(side="right")

    def delete_user(self, user):
        if messagebox.askyesno("Confirm", f"Delete {user.get_username()}?"):
            self.lms.users.remove(user)
            self.lms.save_to_file()
            self.show_users()

    def show_courses(self):
        for w in self.main_work.winfo_children(): w.destroy()
        tk.Label(self.main_work, text="Course Management", font=("Arial", 22, "bold"), bg="#ecf0f1").pack(anchor="w", pady=10)
        tk.Button(self.main_work, text="+ Create New Course", bg=GREEN, fg="white", command=self.create_course_ui).pack(anchor="w", pady=10)

        for c in self.lms.courses:
            f = tk.Frame(self.main_work, bg="white", pady=10, padx=10); f.pack(fill="x", pady=2)
            tk.Label(f, text=f"{c.cid}: {c.title} (Instructor: {c.instructor.get_username()})", bg="white").pack(side="left")
            tk.Button(f, text="Delete", bg=RED, fg="white", command=lambda x=c: self.delete_course(x)).pack(side="right")

    def delete_course(self, course):
        if messagebox.askyesno("Confirm", f"Delete {course.title}?"):
            self.lms.courses.remove(course)
            self.lms.save_to_file()
            self.show_courses()

    def create_course_ui(self):
        pop = tk.Toplevel(self.win); pop.title("New Course"); self.center_window(pop, 400, 300)
        tk.Label(pop, text="Course Title:").pack(pady=5)
        t_ent = tk.Entry(pop); t_ent.pack()

        tk.Label(pop, text="Select Instructor:").pack(pady=5)
        pros = [u.get_username() for u in self.lms.users if u.get_role()=="Instructor"]
        cb = ttk.Combobox(pop, values=pros); cb.pack()

        def save():
            if not t_ent.get() or not cb.get(): return
            inst = next(u for u in self.lms.users if u.get_username() == cb.get())
            new_c = Course(str(100+len(self.lms.courses)), t_ent.get(), inst)
            self.lms.courses.append(new_c)
            inst.assigned_courses.append(new_c)
            self.lms.save_to_file()
            pop.destroy(); self.show_courses()

        tk.Button(pop, text="Create", bg=GREEN, fg="white", command=save).pack(pady=20)

    def show_stats(self):
        for w in self.main_work.winfo_children(): w.destroy()
        tk.Label(self.main_work, text="Global Course Analytics", font=("Arial", 22, "bold"), bg="#ecf0f1").pack(anchor="w", pady=20)

        for c in self.lms.courses:
            row = tk.Frame(self.main_work, bg="white", pady=15, padx=15)
            row.pack(fill="x", pady=5)
            txt = f"Course: {c.title} | Students: {len(c.students)} | Submissions: {len(c.submissions)} | Materials: {len(c.materials)}"
            tk.Label(row, text=txt, font=FONT, bg="white").pack(side="left")

    def show_reports_center(self):
        for w in self.main_work.winfo_children(): w.destroy()
        tk.Label(self.main_work, text="Management Reports", font=("Arial", 22, "bold"), bg="#ecf0f1").pack(anchor="w", pady=20)

        btn_bar = tk.Frame(self.main_work, bg="#ecf0f1")
        btn_bar.pack(fill="x", pady=10)

        display = tk.Text(self.main_work, font=("Consolas", 11), bg="white", height=20)
        display.pack(fill="both", expand=True)

        def run(rep_obj):
            display.delete("1.0", tk.END)
            display.insert(tk.END, rep_obj.generate(self.lms))
            self.lms.log_event(f"Admin generated {rep_obj.__class__.__name__}")

        tk.Button(btn_bar, text="User Audit", command=lambda: run(UserReport())).pack(side="left", padx=5)

    def show_logs(self):
        for w in self.main_work.winfo_children(): w.destroy()

        tk.Label(self.main_work, text="Security Logs", font=("Arial", 22, "bold"), bg="#ecf0f1").pack(anchor="w", pady=10)
        log_box = tk.Text(self.main_work, bg=MAROON, fg="#2ecc71", font=("Consolas", 10))
        log_box.pack(fill="both", expand=True)

        for log in reversed(self.lms.logs): log_box.insert(tk.END, f"> {log}\n")
        log_box.config(state="disabled")

    def show_inbox(self):
        for w in self.main_work.winfo_children(): w.destroy()
        tk.Label(self.main_work, text="Admin Inbox", font=("Arial", 22, "bold"), bg="#ecf0f1").pack(anchor="w", pady=20)

        if not self.user.inbox:
            tk.Label(self.main_work, text="No messages.", bg="#ecf0f1", fg="gray").pack(pady=50)
            return

        for msg in reversed(self.user.inbox):
            f = tk.Frame(self.main_work, bg="white", pady=10, padx=15, relief="solid", bd=1); f.pack(fill="x", pady=5)
            tk.Label(f, text=f"From: {msg.sender} | {msg.subject}", bg="white").pack(side="left")
            tk.Button(f, text="Read", command=lambda m=msg: messagebox.showinfo(m.subject, m.body)).pack(side="right")





    def logout(self):
        self.win.destroy()
        from .auth_gui import LoginGUI
        LoginGUI(self.lms)
