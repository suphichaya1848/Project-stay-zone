# signin_ui_like_mock.py
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap, QCursor
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QPushButton, QLineEdit
)

BILLBOARD_PATH = r"C:/Users/suphi/OneDrive/Desktop/project/photo/Billboard.jpg"

class Login_page(QMainWindow):
    switch_to_sign_up = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("STAY ZONE")
        self.showMaximized()

        # กัน error resize ระหว่างประกอบ UI
        self._ready = False
        self.pm = QPixmap()
        self.board = None

        self._build_ui()
        self._ready = True
        self._layout_on_resize()

    def _build_ui(self):
        root = QWidget()
        self.setCentralWidget(root)

        # สไตล์รวม
        self.setStyleSheet("""
            QMainWindow, QWidget { background:#FFFFFF; }
            QLabel#hello { font:700 44px 'Inter', Arial; color:#111827; }
            QLabel.field { font:600 16px 'Inter', Arial; color:#111827; }
            QLineEdit {
                background:#FFFFFF; border:1px solid #E5E7EB; border-radius:12px;
                padding:10px 14px; font:16px 'Inter', Arial;
            }
            #tab_bg { background:#F3F4F6; border-radius:22px; }
            QPushButton.pill {
                border:1px solid #E5E7EB; border-radius:14px; padding:10px 18px;
                font:600 16px 'Inter', Arial; background:#FFFFFF;
            }
            QPushButton.pill.checked { background:#D2DDFF; border-color:#D2DDFF; }
            QPushButton#btn_login {
                background:#8EA6FF; border:none; border-radius:14px; font:700 16px 'Inter', Arial;
            }
            QLabel.linkblue { color:#176ee8; font:600 15px 'Inter', Arial; }
            QLabel.base { font:500 15px 'Inter', Arial; color:#111827; }
        """)

        # --------- รูปซ้าย ----------
        self.board = QLabel(root)
        self.board.setScaledContents(False)
        self.pm = QPixmap(BILLBOARD_PATH)

        # --------- โลโก้มุมขวาบน ----------
        self.logo = QLabel("Stray\nZONE", root)
        self.logo.setStyleSheet("font:800 20px 'Inter', Arial; color:#111827;")
        self.logo.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)

        # --------- หัวเรื่อง + Tabs ----------
        self.lbl_hello = QLabel("Hello!", root, objectName="hello")

        # กล่องพื้นหลังโค้งมนของแท็บ
        self.tab_bg = QLabel(root, objectName="tab_bg")

        self.tab_signin = QPushButton("Sign in", root)
        self.tab_signin.setProperty("class", "pill checked")   # เลือก Sign in
        self.tab_signin.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        self.tab_signup = QPushButton("Sign Up", root)
        self.tab_signup.setProperty("class", "pill")
        self.tab_signup.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        # --------- ฟอร์ม Sign in ----------
        self.lbl_email = QLabel("Email", root);    self.lbl_email.setProperty("class", "field")
        self.inp_email = QLineEdit(root);          self.inp_email.setPlaceholderText("email@mail.com")

        self.lbl_pass  = QLabel("Password", root); self.lbl_pass.setProperty("class", "field")
        self.inp_pass  = QLineEdit(root);          self.inp_pass.setPlaceholderText("Your password")
        self.inp_pass.setEchoMode(QLineEdit.EchoMode.Password)

        for le in (self.inp_email, self.inp_pass):
            le.setFixedHeight(48)

        self.lnk_forgot = QLabel("<a href='#'>Forgot password?</a>", root)
        self.lnk_forgot.setProperty("class", "linkblue")
        self.lnk_forgot.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)
        self.lnk_forgot.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        self.btn_login = QPushButton("Login", root)
        self.btn_login.setObjectName("btn_login")
        self.btn_login.setFixedHeight(54)
        self.btn_login.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        self.bottom_text = QLabel("Don’t have an account?", root)
        self.bottom_text.setProperty("class", "base")
        self.bottom_link = QLabel("<a href='#' style='text-decoration:none;'>Sign Up here</a>", root)
        self.bottom_link.setProperty("class", "linkblue")
        self.bottom_link.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)
        self.bottom_link.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

    def _layout_on_resize(self):
        if not self._ready or self.board is None or self.pm.isNull():
            return

        W, H = self.width(), self.height()

        # --- ซ้าย: billboard เต็มสูง ---
        left_w = int(W * 0.55)
        self.board.setGeometry(0, 0, left_w, H)
        scaled = self.pm.scaled(
            self.board.size(),
            Qt.AspectRatioMode.KeepAspectRatioByExpanding,
            Qt.TransformationMode.SmoothTransformation
        )
        self.board.setPixmap(scaled)

        # --- ขวา: โซนฟอร์ม ---
        margin = 36
        right_x = left_w + margin
        right_w = max(420, min(560, W - right_x - margin))

        # โลโก้มุมขวาบน
        self.logo.setGeometry(right_x + right_w - 110, 20, 110, 48)

        # คำนวณให้กึ่งกลางแนวตั้ง
        h_hello = self.lbl_hello.sizeHint().height()
        h_tabs  = 44
        total_height = (
            h_hello + 12 + h_tabs + 24 +
            (22 + 16 + 48) +     # Email
            (22 + 16 + 48) +     # Password
            10 + 24 +            # forgot
            18 + 54 +            # Login button
            18 + 24              # bottom line
        )
        top = max(24, int((H - total_height)//2))

        # หัวเรื่อง
        hello_w = self.lbl_hello.sizeHint().width()
        self.lbl_hello.setGeometry(right_x + (right_w - hello_w)//2, top, hello_w, h_hello)

        # กล่องพื้นหลังเม็ดแคปซูลสำหรับแท็บ
        y = top + h_hello + 12
        self.tab_bg.setGeometry(right_x, y-6, right_w, h_tabs + 12)

        # แท็บคู่
        tab_gap = 18
        tab_w = (right_w - tab_gap)//2
        self.tab_signin.setGeometry(right_x + 8, y, tab_w - 8, h_tabs)
        self.tab_signup.setGeometry(right_x + tab_w + tab_gap, y, tab_w - 8, h_tabs)

        # Email
        y += h_tabs + 24
        self.lbl_email.setGeometry(right_x, y, right_w, 22); y += 16
        self.inp_email.setGeometry(right_x, y, right_w, 48)

        # Password
        y += 48 + 16
        self.lbl_pass.setGeometry(right_x, y, right_w, 22); y += 16
        self.inp_pass.setGeometry(right_x, y, right_w, 48)

        # Forgot password? ชิดขวา
        y += 48 + 10
        lnk_w = self.lnk_forgot.sizeHint().width()
        self.lnk_forgot.setGeometry(right_x + right_w - lnk_w, y, lnk_w, 24)

        # ปุ่ม Login
        y += 24 + 18
        self.btn_login.setGeometry(right_x, y, right_w, 54)

        # บรรทัดล่าง
        y += 54 + 18
        base_w = self.bottom_text.sizeHint().width()
        link_w = self.bottom_link.sizeHint().width()
        total_w = base_w + 8 + link_w
        base_x = right_x + (right_w - total_w)//2
        self.bottom_text.setGeometry(base_x, y, base_w, 24)
        self.bottom_link.setGeometry(base_x + base_w + 8, y, link_w, 24)

    def resizeEvent(self, event):
        if getattr(self, "_ready", False):
            self._layout_on_resize()
        super().resizeEvent(event)


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    w = Login_page()
    w.show()
    sys.exit(app.exec())
