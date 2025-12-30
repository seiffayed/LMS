import re

class Validator:
    @staticmethod
    def validate_gmail(email):
        return re.match(r"[^@]+@gmail\.com$", email)

    @staticmethod
    def validate_password(password):
        return len(password) >= 6
