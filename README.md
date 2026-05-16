1- PROJECT DESCRIPTION:
This LMS is designed by python to bridge the gap between educators and learners. It provides a centralized platform where an admin manages the system, instructors post content and evaluate performance, and students engage with materials and track their academic progress. The application ensures data persistence using a local SQLite database, allowing users to pick up exactly where they left off.

2- FEATURES:
User Authentication & Security:
- Role-Based Access Control: Separate dashboards for Admin, Instructor, and Student.
- Validation: Regex-based email validation (strictly @gmail.com) and password strength checks.
- Secure Storage: User credentials and system state are managed through a persistent SQLite backend.

Administrator Dashboard
- System Overview: Real-time statistics on total users, courses, and students.
- User Management: Ability to view and remove users from the system.
- Course Management: Create new courses and assign them to specific instructors.
- Security Logs: View a detailed history of all system events and logins.
- Reports Center: Generate automated User Audit reports.

Instructor Dashboard
- Content Creation: Upload lecture materials (supports PDF/File attachments) and post announcements.
- Assignment Management: Create tasks with maximum marks.
- Grading Center: Review student submissions and assign grades with automated notifications.
- Academic Reporting: Generate detailed individual progress reports for students, including assignment averages and performance.

Student Dashboard
- Enrollment: Browse the course catalog and join classrooms.
- Digital Classroom: Access notice boards, view study materials, and view assignment details.
- Task Submission: Submit work directly through the interface.
- Notifications: Get instant alerts for new materials, assignments, and grades.

Communication System
- Private Messaging: Integrated inbox for all users to send and receive messages.
- Read/Unread Status: Track message status.

Technical Architecture
- GUI: Built using tkinter and ttk for a modern, responsive feel.
- Database: sqlite3 for local data persistence.
- Design includes:
Inheritance: Admin, Instructor, and Student inherit from a User base class.
Abstraction: Uses Abstract Base Classes (ABC) for reports and content models.
Encapsulation: Private attributes such as in (__password, __grades).

3- HOW TO RUN THE PROJECT:
Prerequisites:
- Python installed on your machine.
- Tkinter (usually comes pre-installed with Python, but Linux users may need to install python3-tk).

Steps to Run:
- Clone the Repository:
```bash
git clone https://github.com/ShahdHamdy386/LMS_.git
```
- Navigate to the Project Directory:
```bash
cd LMS_
```
- Run the Application:
```bash
python main.py
```

Default Credentials (for first-time boot):
- Admin: Username: admin | Password: admin123
- Instructor: Username: pro | Password: pro123
- Student: Username: student | Password: stud123

4- SCREEN SHOTS:
GENERAL: 
- login gui
![login gui](images/LOGIN.png)

- create user
![create user](images/CREATE%20USER.png)

ADMIN:
- admin dashboard and system overview
![admin dashboard and system overview](images/admin/ADMIN%20DASHBOARD%20AND%20SYSTEM%20OVERVIEW.png)

- course analysis
![course analysis](images/admin/COURSE%20ANALYSIS.png)

- course management
![course management](images/admin/COURSE%20MANAGEMENT.png)

- management reports
![management reports](images/admin/MANAGEMENT%20REPORTS.png)

- security logs
![security logs](images/admin/SECURITY%20LOGS.png)

STUDENT:
- enroll courses
![enroll courses](images/student/ENROLL%20COURSES.png)

- inbox
![inbox](images/student/INBOX.png)

- messages
![messages](images/student/MESSAGES.png)

- my classrooms
![my classrooms](images/student/MY%20CLASSROOMS.png)

INSTRUCTOR:
- add assignment
![add assignment](images/INSTRUCTOR/ADD%20ASSIGNMENT.png)

- add material
![add material](images/INSTRUCTOR/ADD%20MATERIAL.png)

- announcements 
![announcements](images/INSTRUCTOR/ANNOUNCEMENTS.png)

- grading center 
![grading center](images/INSTRUCTOR/GRADING%20CENTER.png)

- manage courses
![manage courses](images/INSTRUCTOR/MANAGE%20COURSES.png)

5- TEAM MEMBERS AND CONTRIBUTIONS:

MEMBER 1:
- Shahd Hamdy - 120230070  
- data base management, main 
- code files: models/database_manager.py , main.py

MEMBER 2: 
- Ahmed Osama - 120230014
- instructor GUI
- code files: gui/instructor_gui.py

MEMBER 3: 
- Hala Mostafa - 120230148
- student GUI
- code files: gui/student_gui.py

MEMBER 4: 
- Seif Fayed - 120230091
- admin GUI, report models
- code files: gui/admin_gui.py , models/report_models.py

MEMBER 5: 
- Marisia Michael - 120230233
- colors, validators, base window, lms system, register and login GUI
- code files: color.py , validators.py , gui/base_window.py , models/lms_system.py , gui/auth_gui.py

MEMBER 6: 
- Mariam Gamal - 120230012
- abc models , content models , user models , course models
- code files: models/abc_models.py , models/content_models.py , models/user_models.py , models/course_models.py

6- ADDITIONAL NOTES:
- Data Storage: 
All data is saved in a file named lms_data.db. If this file is deleted, the system will re-initialize with default accounts.

Dependencies
- sqlite3 (Built-in)
- tkinter (Built-in)
- re (For email validation)

