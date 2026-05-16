import tkinter as tk
from tkinter import messagebox
from .base_window import BaseWindow
from color import MAROON, BROWN, GREEN, FONT
from validators import Validator

class RegisterGUI(BaseWindow):
    def __init__(self, lms):
        self.lms = lms
        self.win = tk.Tk()
        self.win.title("Create LMS Account")
        self.center_window(self.win, 400, 500)
        self.win.configure(bg="white")
        tk.Label(self.win, text="Join the Platform", font=("Arial", 20, "bold"), bg="white", fg=MAROON).pack(pady=30)
        self.u_ent = self.create_field("Username")
        self.e_ent = self.create_field("Gmail Address")
        self.p_ent = self.create_field("Password", True)
        tk.Label(self.win, text="I am a:", bg="white").pack()
        self.role_var = tk.StringVar(value="Student")
        tk.OptionMenu(self.win, self.role_var, "Student", "Instructor").pack(pady=10)
        tk.Button(self.win, text="CREATE ACCOUNT", bg=GREEN, fg="white", font=FONT, command=self.handle_reg).pack(fill="x", padx=50, pady=20)
        tk.Button(self.win, text="Back to Login", fg=BROWN, bg="white", bd=0, command=self.back).pack()

    def create_field(self, label, is_pass=False):
        tk.Label(self.win, text=label, bg="white").pack()
        e = tk.Entry(self.win, show="*" if is_pass else "", font=("Arial", 12), bd=1, relief="solid")
        e.pack(fill="x", padx=50, pady=5, ipady=3)
        return e

    def handle_reg(self):
        u, e, p, r = self.u_ent.get(), self.e_ent.get(), self.p_ent.get(), self.role_var.get()
        if not Validator.validate_gmail(e):
            return messagebox.showerror("Error", "Invalid Email! Must be @gmail.com")
        if not Validator.validate_password(p):
            return messagebox.showerror("Error", "Password too short (min 6 chars)")
        success, msg = self.lms.register_user(u, p, e, r)
        if success:
            self.lms.save_to_file()
            messagebox.showinfo("Success", "Account Created! Please log in.")
            self.back()
        else:
            messagebox.showerror("Error", msg)

    def back(self):
        self.win.destroy()
        LoginGUI(self.lms)

class LoginGUI(BaseWindow):
    def __init__(self, lms):
        self.lms = lms
        self.root = tk.Tk()
        self.root.title("LMS Gateway")
        self.maximize_window(self.root)
        self.root.configure(bg="white")

        tk.Label(self.root, text="LMS", font=("Arial", 40, "bold"), bg=MAROON, fg="white").pack(fill="x", pady=(0,20))
        tk.Label(self.root, text="Username", bg="white").pack(pady=(20,0))
        self.u = tk.Entry(self.root, font=("Arial", 12))
        self.u.pack(pady=5, ipady=3)
        tk.Label(self.root, text="Password", bg="white").pack()
        self.p = tk.Entry(self.root, show="*", font=("Arial", 12))
        self.p.pack(pady=5, ipady=3)
        tk.Button(self.root, text="LOGIN", bg=BROWN, fg="white", font=FONT, command=self.login, width=15).pack(pady=20)
        tk.Button(self.root, text="Create Account", fg=MAROON, bg="white", bd=0, command=self.open_reg).pack()
        self.root.mainloop()

    def login(self):
        user = self.lms.authenticate(self.u.get(), self.p.get())
        if user:
            self.root.destroy()
            # Local imports to avoid circular dependency
            if user.get_role() == "Admin":
                from .admin_gui import AdminDashboard
                AdminDashboard(user, self.lms)
            elif user.get_role() == "Instructor":
                from .instructor_gui import InstructorDashboard
                InstructorDashboard(user, self.lms)
            else:
                from .student_gui import StudentDashboard
                StudentDashboard(user, self.lms)
        else:
            messagebox.showerror("Failed", "Login Error")

    def open_reg(self):
        self.root.destroy()
        RegisterGUI(self.lms)
