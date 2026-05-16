from models.lms_system import LMS
from gui.auth_gui import LoginGUI

if __name__ == "__main__":
    global_lms = LMS()
    LoginGUI(global_lms)
