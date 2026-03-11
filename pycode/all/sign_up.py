from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap, QCursor
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QPushButton, QLineEdit

BILLBOARD_PATH = r"C:/Users/suphi/OneDrive/Desktop/project/photo/Billboard.jpg"

class Login_page(QMainWindow):
    switch_to_sign_up = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("STAY ZONE")
        self.showMaximized()

        # กัน error ตอน resize ระหว่างประกอบ UI
        self._ready = False
        self.pm = QPixmap()
        self.board = None

        self._build_ui()
        self._ready = True
        self._layout_on_resize()

    def _build_ui(self):
        root = QWidget()
        self.setCentralWidget(root)

        # พื้นหลังขาว
        self.setStyleSheet("""
            QMainWindow, QWidget { background: #FFFFFF; }
            QLabel#hello { font: 700 44px 'Inter', Arial; color:#111827; }
            QLabel.field { font: 600 16px 'Inter', Arial; color:#111827; }
            QLineEdit {
                background:#FFFFFF; border:1px solid #E5E7EB; border-radius:12px;
                padding:10px 14px; font:16px 'Inter', Arial;
            }
            QPushButton.pill {
                border:1px solid #E5E7EB; border-radius:16px; padding:10px 18px;
                font:600 16px 'Inter', Arial; background:#FFFFFF;
            }
            QPushButton.pill.checked { background:#DDE5FF; border-color:#DDE5FF; }
            #tab_bg {
                background:#F3F4F6; border-radius:20px;    /* กล่องเม็ดแคปซูลรวม 2 ปุ่ม */
            }
            QPushButton#btn_signup_main {
                background:#8EA6FF; border:none; border-radius:14px; font:700 16px 'Inter', Arial;
            }
            QLabel.linkblue { color:#176ee8; font:600 15px 'Inter', Arial; }
            QLabel.base { font:500 15px 'Inter', Arial; color:#111827; }
        """)

        # ---------- รูปซ้าย ----------
        self.board = QLabel(root)
        self.board.setScaledContents(False)
        self.pm = QPixmap(BILLBOARD_PATH)

        # ---------- โลโก้มุมขวาบน ----------
        self.logo = QLabel("Stray\nZONE", root)
        self.logo.setStyleSheet("font: 800 20px 'Inter', Arial; color:#111827;")
        self.logo.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)

        # ---------- หัวเรื่อง + Tabs ----------
        self.lbl_hello = QLabel("Hello!", root, objectName="hello")

        # พื้นหลัง pill รวม 2 ปุ่ม
        self.tab_bg = QLabel(root, objectName="tab_bg")
        self.tab_signin = QPushButton("Sign in", root)
        self.tab_signin.setProperty("class", "pill")
        self.tab_signin.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        self.tab_signup = QPushButton("Sign Up", root)
        self.tab_signup.setProperty("class", "pill checked")   # เลือก Sign Up ตามภาพ
        self.tab_signup.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        # ---------- ฟอร์ม Sign Up ----------
        self.lbl_name  = QLabel("Name", root);          self.lbl_name.setProperty("class", "field")
        self.inp_name  = QLineEdit(root);               self.inp_name.setPlaceholderText("Enter your name")

        self.lbl_phone = QLabel("Phone number", root);  self.lbl_phone.setProperty("class", "field")
        self.inp_phone = QLineEdit(root);               self.inp_phone.setPlaceholderText("Phone")

        self.lbl_email = QLabel("Email", root);         self.lbl_email.setProperty("class", "field")
        self.inp_email = QLineEdit(root);               self.inp_email.setPlaceholderText("email@mail.com")

        self.lbl_pass  = QLabel("Password", root);      self.lbl_pass.setProperty("class", "field")
        self.inp_pass  = QLineEdit(root);               self.inp_pass.setPlaceholderText("Your password")
        self.inp_pass.setEchoMode(QLineEdit.EchoMode.Password)

        for le in (self.inp_name, self.inp_phone, self.inp_email, self.inp_pass):
            le.setFixedHeight(48)

        self.btn_signup = QPushButton("Sign Up", root)
        self.btn_signup.setObjectName("btn_signup_main")
        self.btn_signup.setFixedHeight(54)
        self.btn_signup.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        self.bottom_text = QLabel("Already have an account?", root)
        self.bottom_text.setProperty("class", "base")
        self.bottom_link = QLabel("<a href='#' style='text-decoration:none;'>Sign in</a>", root)
        self.bottom_link.setProperty("class", "linkblue")
        self.bottom_link.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)
        self.bottom_link.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

    def _layout_on_resize(self):
        if not self._ready or self.board is None or self.pm.isNull():
            return

        W, H = self.width(), self.height()

        # ----- ซ้าย: billboard เต็มสูง -----
        left_w = int(W * 0.55)
        self.board.setGeometry(0, 0, left_w, H)
        scaled = self.pm.scaled(self.board.size(),
                                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                                Qt.TransformationMode.SmoothTransformation)
        self.board.setPixmap(scaled)

        # ----- ขวา: พื้นที่แบบฟอร์ม -----
        margin = 36
        right_x = left_w + margin
        right_w = max(420, min(560, W - right_x - margin))

        # โลโก้มุมขวาบน
        self.logo.setGeometry(right_x + right_w - 110, 18, 110, 48)

        # คำนวณความสูงรวมเพื่อจัดกึ่งกลางแนวตั้ง
        h_hello = self.lbl_hello.sizeHint().height()      # ~ 52
        h_tabs  = 44
        rows = 4
        total_height = (
            h_hello + 12 +
            h_tabs + 20 +
            rows*(22 + 16 + 48) +    # (label + spacing + input)*4
            18 + 54 +                # ปุ่ม
            16 + 24                  # บรรทัดล่าง
        )
        top = max(24, int((H - total_height)//2))

        # Hello! กึ่งกลาง
        hello_w = self.lbl_hello.sizeHint().width()
        self.lbl_hello.setGeometry(right_x + (right_w - hello_w)//2, top, hello_w, h_hello)

        # กล่องพื้นหลัง pill สำหรับ 2 ปุ่ม
        y = top + h_hello + 12
        pill_h = h_tabs + 12
        self.tab_bg.setGeometry(right_x, y-6, right_w, pill_h)  # ทำให้ดูมี padding รอบๆ
        # สองปุ่มในกล่อง pill
        tab_gap = 12
        tab_w = (right_w - tab_gap)//2
        self.tab_signin.setGeometry(right_x + 8, y, tab_w - 8, h_tabs)
        self.tab_signup.setGeometry(right_x + tab_w + tab_gap, y, tab_w - 8, h_tabs)

        # ฟอร์ม Name
        y += h_tabs + 20
        self.lbl_name.setGeometry(right_x, y, right_w, 22); y += 16
        self.inp_name.setGeometry(right_x, y, right_w, 48)

        # Phone
        y += 48 + 16
        self.lbl_phone.setGeometry(right_x, y, right_w, 22); y += 16
        self.inp_phone.setGeometry(right_x, y, right_w, 48)

        # Email
        y += 48 + 16
        self.lbl_email.setGeometry(right_x, y, right_w, 22); y += 16
        self.inp_email.setGeometry(right_x, y, right_w, 48)

        # Password
        y += 48 + 16
        self.lbl_pass.setGeometry(right_x, y, right_w, 22); y += 16
        self.inp_pass.setGeometry(right_x, y, right_w, 48)

        # ปุ่ม Sign Up
        y += 48 + 18
        self.btn_signup.setGeometry(right_x, y, right_w, 54)

        # บรรทัดล่าง
        y += 54 + 16
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
