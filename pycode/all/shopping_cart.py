# shopping_cart_ui_only_separate_count.py
# -----------------------------------------------------
# UI ตะกร้าสินค้า (ไม่มีระบบ) แยกจำนวนการ์ดสินค้าออกจากคลาส
# - TopBar      : แถบนำทางบนสุด (class แยก)
# - CartItemCard: การ์ดสินค้า 1 ใบ (class แยก)
# - ShoppingCartWindow: จัดวางหน้า โดย "รับจำนวน/รายการสินค้า" จากภายนอก
# -----------------------------------------------------

BANNER_PATH = r"C:/Users/suphi/OneDrive/Desktop/project/photo/Checkout.png"
LOGO_PATH  = "C:/Users/suphi/OneDrive/Desktop/project/photo/logo.jpg"

from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QPixmap, QColor
from PyQt6.QtWidgets import (
    QApplication, QWidget, QMainWindow, QLabel, QHBoxLayout, QVBoxLayout,
    QFrame, QToolButton, QPushButton, QSizePolicy, QStyle, QGraphicsDropShadowEffect,
    QScrollArea
)

# (ทางเลือก) ใส่โลโก้/รูปสินค้าได้เองภายหลัง
LOGO_PATH  = "C:/Users/suphi/OneDrive/Desktop/project/photo/logo.jpg"   # path โลโก้
ITEM_IMAGE = ""   # path รูปสินค้า


# ============================================================
# Class 1 : TopBar (UI-only)
# ============================================================
class TopBar(QWidget):
    """แถบเมนูด้านบน (ลอย + เงานุ่ม) — UI-only"""
    def __init__(self, parent=None):
        super().__init__(parent)

        outer = QHBoxLayout(self)
        outer.setContentsMargins(10, 10, 10, 0)

        bar = QFrame()
        bar.setObjectName("TopBar")
        bar.setMinimumHeight(64)

        # เงานุ่ม
        shadow = QGraphicsDropShadowEffect(blurRadius=12, xOffset=0, yOffset=2)
        shadow.setColor(QColor(0, 0, 0, 58))
        bar.setGraphicsEffect(shadow)

        h = QHBoxLayout(bar)
        h.setContentsMargins(18, 10, 18, 10)
        h.setSpacing(16)

        # โลโก้ (placeholder)
        logo = QLabel()
        logo.setFixedSize(100, 36)
        logo.setStyleSheet("border:1px dashed #DDD; border-radius:8px; background:#FFF;")
        if LOGO_PATH:
            pm = QPixmap(LOGO_PATH)
            if not pm.isNull():
                logo.setPixmap(pm.scaled(100, 36, Qt.AspectRatioMode.KeepAspectRatio))
        h.addWidget(logo)
        h.addSpacing(10)

        # เมนู
        for name in ["Home", "Albums", "Skzoo", "Fashion", "All"]:
            btn = QToolButton(); btn.setText(name); btn.setAutoRaise(True); btn.setObjectName("NavBtn")
            h.addWidget(btn)
        h.addStretch(1)

        # ไอคอน (placeholder)
        def icon_btn(sp):
            b = QToolButton(); b.setAutoRaise(True)
            b.setIcon(QApplication.style().standardIcon(sp)); b.setIconSize(QSize(18, 18))
            return b
        h.addWidget(icon_btn(QStyle.StandardPixmap.SP_FileDialogContentsView))
        h.addWidget(icon_btn(QStyle.StandardPixmap.SP_DialogYesButton))
        h.addWidget(icon_btn(QStyle.StandardPixmap.SP_DirHomeIcon))

        outer.addWidget(bar)

        self.setStyleSheet("""
        #TopBar { background:white; border-radius:16px; border:1px solid #e9e9ef; }
        QToolButton#NavBtn { font:500 14px "Inter"; color:#2a2a2a; padding:6px 10px; }
        QToolButton#NavBtn:hover { background:#f3f4f7; border-radius:8px; }
        """)


# ============================================================
# Class 2 : CartItemCard (UI-only)
# ============================================================
class CartItemCard(QFrame):
    """การ์ดสินค้า 1 ใบ (UI-only)"""
    def __init__(self, title: str, price_text: str = "650 บาท", image_path: str = "", parent=None):
        super().__init__(parent)

        self.setObjectName("CartItem")

        root = QHBoxLayout(self)
        root.setContentsMargins(16, 12, 16, 12)
        root.setSpacing(16)

        # ซ้าย: รูปสินค้า (หรือคำว่า Image)
        image_box = QFrame(); image_box.setObjectName("ImageBox")
        image_box.setMinimumSize(130, 130); image_box.setMaximumSize(130, 130)
        iv = QVBoxLayout(image_box); iv.setContentsMargins(0, 0, 0, 0); iv.setAlignment(Qt.AlignmentFlag.AlignCenter)
        img = QLabel(); img.setAlignment(Qt.AlignmentFlag.AlignCenter); img.setObjectName("ImageLabel")
        if image_path:
            pm = QPixmap(image_path)
            if not pm.isNull():
                img.setPixmap(pm.scaled(120, 120, Qt.AspectRatioMode.KeepAspectRatio))
            else:
                img.setText("Image")
        else:
            img.setText("Image")
        iv.addWidget(img)

        # ขวา: รายละเอียด
        content = QFrame()
        cl = QVBoxLayout(content); cl.setContentsMargins(0, 4, 0, 0); cl.setSpacing(8)

        # ปุ่มลบ (UI เท่านั้น)
        top = QHBoxLayout(); top.addStretch(1)
        trash = QToolButton(); trash.setAutoRaise(True)
        trash.setIcon(QApplication.style().standardIcon(QStyle.StandardPixmap.SP_TrashIcon))
        trash.setIconSize(QSize(18, 18))
        top.addWidget(trash)

        title_lbl = QLabel(title); title_lbl.setObjectName("Title"); title_lbl.setWordWrap(True)

        bottom = QHBoxLayout(); bottom.setSpacing(8)
        minus = QToolButton(); minus.setObjectName("QtyBtn"); minus.setText("−"); minus.setAutoRaise(True)
        qty   = QLabel("1");   qty.setObjectName("Qty"); qty.setAlignment(Qt.AlignmentFlag.AlignCenter); qty.setMinimumWidth(18)
        plus  = QToolButton(); plus.setObjectName("QtyBtn");  plus.setText("+"); plus.setAutoRaise(True)
        price = QLabel(price_text); price.setObjectName("Price")

        bottom.addStretch(1)
        bottom.addWidget(minus); bottom.addWidget(qty); bottom.addWidget(plus)
        bottom.addSpacing(12)
        bottom.addWidget(price, 0, Qt.AlignmentFlag.AlignRight)

        cl.addLayout(top)
        cl.addWidget(title_lbl)
        cl.addStretch(1)
        cl.addLayout(bottom)

        root.addWidget(image_box)
        root.addWidget(content, 1)

        self.setStyleSheet("""
        #CartItem { background:white; border-radius:10px; border:1px solid rgba(0,0,0,20); }
        #ImageBox { background:#f4f5f7; border-radius:8px; border:1px dashed #d7d9de; }
        #ImageLabel { color:#9aa0a6; font:500 12px "Inter"; }
        #Title { font:500 14px "Inter"; color:#222; }
        #Qty   { font:500 13px "Inter"; color:#333; padding:2px 6px; }
        #Price { font:600 13px "Inter"; color:#111; }
        QToolButton#QtyBtn { font:700 14px "Inter"; padding:2px 6px; border-radius:6px; border:1px solid #e1e2e6; background:#fafafa; }
        QToolButton#QtyBtn:hover { background:#f0f0f3; }
        """)


# ============================================================
# หน้าหลัก: รับ "จำนวนการ์ด" (หรือ "ลิสต์รายการ") จากภายนอก
# ============================================================
class ShoppingCartWindow(QMainWindow):
    """
    - UI-only
    - จำนวนการ์ดสินค้า "ไม่ถูกกำหนดในคลาส" แต่รับมาจากภายนอกผ่าน
      - items_count: จำนวนการ์ดที่ต้องการสร้างแบบใช้ template เดียวกัน
      - หรือ items: ลิสต์ dict [{'title':.., 'price_text':.., 'image_path':..}, ...]
    """
    def __init__(self, items_count: int | None = None, items: list[dict] | None = None):
        super().__init__()
        self.setWindowTitle("Shopping Cart - UI Only")
        self.resize(1120, 860)

        central = QWidget(); self.setCentralWidget(central)
        root = QVBoxLayout(central); root.setContentsMargins(16, 12, 16, 16); root.setSpacing(12)

        # TopBar
        root.addWidget(TopBar(), 0)

        # Body (ซ้าย/ขวา)
        body = QHBoxLayout(); body.setSpacing(22); body.setContentsMargins(4, 0, 4, 0)
        root.addLayout(body, 1)

        # ---------- ซ้าย: หัวเรื่อง + scroll ของการ์ด ----------
        left = QVBoxLayout(); left.setSpacing(14)
        title = QLabel("Shopping Cart"); title.setStyleSheet('font:700 26px "Inter"; color:#1f1f1f;')
        hr = QFrame(); hr.setFrameShape(QFrame.Shape.HLine); hr.setStyleSheet("color:#e7e7ea;"); hr.setFixedHeight(2)
        left.addWidget(title); left.addWidget(hr)

        scroll = QScrollArea(); scroll.setWidgetResizable(True); scroll.setStyleSheet("QScrollArea{border:none;}")
        wrap = QWidget(); cards = QVBoxLayout(wrap); cards.setSpacing(12); cards.setContentsMargins(0, 0, 0, 0)

        # >>>>>>> จุดนี้: ตัดสินใจ "จำนวนการ์ด" จากภายนอก <<<<<<<
        if items is not None:
            # ให้มากำหนดเป็นลิสต์ของสินค้าเอง
            for it in items:
                cards.addWidget(CartItemCard(
                    title=it.get("title", "Untitled"),
                    price_text=it.get("price_text", "0 บาท"),
                    image_path=it.get("image_path", ITEM_IMAGE)
                ))
        else:
            # ถ้าไม่ส่งลิสต์มา ใช้จำนวนการ์ดจาก items_count (ค่าเริ่มต้น = 4)
            count = 4 if items_count is None else max(0, int(items_count))
            for _ in range(count):
                cards.addWidget(CartItemCard("Stray Kids - ATE [9th Mini Album]", "650 บาท", image_path=ITEM_IMAGE))

        cards.addStretch(1)
        scroll.setWidget(wrap)
        left.addWidget(scroll, 1)
        body.addLayout(left, 1)

        # ---------- ขวา: กล่องสรุป (UI-only) ----------
        right = QVBoxLayout(); right.setAlignment(Qt.AlignmentFlag.AlignTop)
        summary = QFrame(); summary.setObjectName("SummaryCard"); summary.setFixedWidth(320)
        sv = QVBoxLayout(summary); sv.setContentsMargins(18, 16, 18, 16); sv.setSpacing(10)
        st = QLabel("Order Summary"); st.setStyleSheet('font:600 16px "Inter"; color:#1f1f1f;')
        sv.addWidget(st); sv.addWidget(QLabel("Items   2")); sv.addWidget(QLabel("Subtotal 1,300")); sv.addWidget(QLabel("Shipping 45"))
        hr2 = QFrame(); hr2.setFrameShape(QFrame.Shape.HLine); hr2.setStyleSheet("color:#ececf2;"); sv.addWidget(hr2)
        tot = QLabel("Total   1,345 บาท"); tot.setStyleSheet('font:700 18px "Inter"; color:#111;'); sv.addWidget(tot)
        btn = QPushButton("Checkout"); btn.setFixedHeight(38); btn.setStyleSheet("QPushButton{font:600 14px 'Inter'; background:#3165ff; color:#fff; border:none; border-radius:20px;}")
        sv.addWidget(btn)
        right.addWidget(summary, 0, Qt.AlignmentFlag.AlignTop)
        body.addLayout(right, 0)

        central.setStyleSheet('QWidget { background:#fbfbfd; font-family:"Inter","Segoe UI","Tahoma"; }')
        summary.setStyleSheet("#SummaryCard{background:#fff; border:1px solid rgba(0,0,0,20); border-radius:12px;}")

# ------------------------------------------------------------
# ใช้งานจริง: กำหนด "จำนวนการ์ด" หรือ "ลิสต์สินค้า" จากภายนอก
# ------------------------------------------------------------
if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)

    ITEM_COUNT = 2
    win = ShoppingCartWindow(items_count=ITEM_COUNT)
    win.show()
    sys.exit(app.exec())







