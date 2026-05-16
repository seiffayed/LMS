from abc import ABC, abstractmethod
from datetime import datetime

class SystemReport(ABC):
    @abstractmethod
    def generate(self, lms_obj):
        pass

class UserReport(SystemReport):
    def generate(self, lms_obj):
        report = f"USER AUDIT REPORT - {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
        report += "="*50 + "\n"
        report += f"{'Role':<12} | {'Username':<15} | {'Email'}\n"
        report += "-"*50 + "\n"
        for u in lms_obj.users:
            report += f"{u.get_role():<12} | {u.get_username():<15} | {u.get_email()}\n"
        return report

