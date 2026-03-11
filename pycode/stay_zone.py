import os, re, sys, sqlite3, random, subprocess, webbrowser
from datetime import datetime
import datetime as _dt  
import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog, ttk
import customtkinter as ct
from customtkinter import CTkImage
from PIL import Image, ImageTk, ImageOps, ImageDraw
from reportlab.pdfgen import canvas as pdf_canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.fonts import addMapping

#สี
WHITE      = "#ffffff"
BLUE_LIGHT = "#bed5ff"
BLUE_DARK  = "#7facff"
GRAY_LIGHT = "#f7f7f7"
GRAY_DARK  = "#d9d9d9"

ct.set_appearance_mode("light")
ct.set_default_color_theme("blue")

#ฐานข้อมูล
DB_PATH = r"C:/Users/suphi/OneDrive/Desktop/project/pycode/stay_zone_data.db"

#Font
APP_FONT_FAMILY = "CMU-Regular"  
def F(size=20, weight=None):
    return ct.CTkFont(family=APP_FONT_FAMILY, size=size, weight=weight)
try:
    ct.ThemeManager.theme["CTkFont"]["family"] = APP_FONT_FAMILY
    ct.ThemeManager.theme["CTkFont"]["size"] = 14
except Exception:
    pass


#ui 

# กรอบรูปภาพ
def image_widget(parent, path, w, h, corner=16): 
    box = ct.CTkFrame(parent, fg_color=WHITE, width=w, height=h, corner_radius=corner)
    box.grid_propagate(False)
    try:
        if path and os.path.exists(path):
            img = Image.open(path).resize((w, h), Image.LANCZOS)
            tkimg = ImageTk.PhotoImage(img)
            lbl = tk.Label(box, image=tkimg, border=0, highlightthickness=0, bg=WHITE)
            lbl.image = tkimg
            lbl.place(relx=0.5, rely=0.5, anchor="center")
            return box
    except Exception:
        pass
    ct.CTkLabel(box, text="ไม่มีรูป", font=F(16), text_color="#666666")\
      .place(relx=0.5, rely=0.5, anchor="center")
    return box

def circle_avatar_image(path: str|None, size=44):
    
    try:
        if path and os.path.exists(path):
            im = Image.open(path).convert("RGBA")
        else:
            im = Image.new("RGBA", (size, size), (230,230,230,255))
        im = ImageOps.fit(im, (size, size), Image.LANCZOS)
        mask = Image.new("L", (size, size), 0)
        ImageDraw.Draw(mask).ellipse((0,0,size-1,size-1), fill=255)
        im.putalpha(mask)
        return CTkImage(light_image=im, size=(size, size))  # ✅ ใช้ CTkImage
    except Exception:
        ph = Image.new("RGBA", (size, size), (230,230,230,255))
        return CTkImage(light_image=ph, size=(size, size))

#สร้างรูปภาพวงกลม
def make_ctk_circle_image(path: str | None, size=140):
    
    try:
        if path and os.path.exists(path):
            im = Image.open(path).convert("RGBA")
        else:
            im = Image.new("RGBA", (size, size), (230,230,230,255))
        im = ImageOps.fit(im, (size, size), Image.LANCZOS)
        mask = Image.new("L", (size, size), 0)
        ImageDraw.Draw(mask).ellipse((0, 0, size-1, size-1), fill=255)
        im.putalpha(mask)
        return CTkImage(light_image=im, size=(size, size))
    except Exception:
        ph = Image.new("RGBA", (size, size), (230,230,230,255))
        return CTkImage(light_image=ph, size=(size, size))



#ซ่อนสกอร์บาร์
def hide_scrollbar(sf):
    try:
        sb = getattr(sf, "_scrollbar", None) or getattr(sf, "scrollbar", None)
        if sb:
            try: sb.grid_forget()
            except Exception:
                try: sb.pack_forget()
                except Exception: pass
            try: sb.configure(width=0)
            except Exception: pass
    except Exception:
        pass


#รูปหน้า sidn in / up
class LeftImage(ct.CTkFrame):
    def __init__(self, master, image_path=None):
        super().__init__(master, fg_color=WHITE)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        if image_path and os.path.exists(image_path):
            try:
                img = Image.open(image_path)

            
                screen_h = master.winfo_screenheight()
                max_h = int(screen_h * 1.15)  #ปรับขนาดรูป
                if img.height > max_h:
                    new_w = int(img.width * (max_h / img.height))
                    img = img.resize((new_w, max_h), Image.LANCZOS)

                tkimg = ImageTk.PhotoImage(img)
                lbl = tk.Label(self, image=tkimg, border=0, highlightthickness=0, bg=WHITE)
                lbl.image = tkimg

                # วางรูปชิดขอบล่างซ้าย
                lbl.place(relx=0.0, rely=1.0, anchor="sw")   
            except Exception:
                tk.Label(self, text="", bg=WHITE).grid(row=0, column=0, sticky="nsew")
        else:
            tk.Label(self, text="", bg=WHITE).grid(row=0, column=0, sticky="nsew")



#สร้างฐานข้อมูล
class ShopDB:

    def __init__(self, path=DB_PATH):
        self.conn = sqlite3.connect(path)
        self.c = self.conn.cursor()
        self._init_users()
        self._init_products()
        self._init_purchase_history()
        self._init_orders()

    #ตาราง users
    def _init_users(self):
        self.c.execute("""
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                password TEXT,
                email    TEXT,
                profile_image TEXT
            )
        """)
        self.conn.commit()

    #ตารางสินค้า
    def _init_products(self):
        self.c.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id    INTEGER PRIMARY KEY,
                name  TEXT,
                price INTEGER,
                stock INTEGER,
                image_path TEXT
            )
        """)
        self.conn.commit()

    #ตารางประวัติการซื้อ
    def _init_purchase_history(self):
        self.c.execute("""
            CREATE TABLE IF NOT EXISTS purchase_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT,
                product_name TEXT,
                quantity INTEGER,
                total_price INTEGER,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (username) REFERENCES users(username)
            )
        """)
        self.conn.commit()

    #ตารางคำสั่งซื้อ
    def _init_orders(self):
        self.c.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id TEXT UNIQUE,
                username TEXT,
                customer_name TEXT,
                phone TEXT,
                address TEXT,
                total INTEGER,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                payment_image TEXT
            )
        """)
        
        # ตารางรายการสินค้าในคำสั่งซื้อ
        self.c.execute("""
            CREATE TABLE IF NOT EXISTS order_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id TEXT,
                product_id INTEGER,
                product_name TEXT,
                qty INTEGER,
                price_each INTEGER,
                sub_total INTEGER
            )
        """)
        self.conn.commit()
        
        # เพิ่มคอลัมน์ is_done ถ้ายังไม่มี
        try:
            self.c.execute("ALTER TABLE orders ADD COLUMN is_done INTEGER DEFAULT 0")
            self.conn.commit()
        except sqlite3.OperationalError:
            pass  # มีคอลัมน์แล้ว




    # users
    def update_user_profile(self, old_username: str, new_username: str, new_email: str, new_profile_image: str | None):
        # ตรวจ username email ซ้ำ
        if new_username != old_username:
            self.c.execute("SELECT 1 FROM users WHERE username=?", (new_username,))
            if self.c.fetchone():
                return False, "Username นี้ถูกใช้แล้ว"
        self.c.execute("SELECT 1 FROM users WHERE email=? AND username<>?", (new_email, old_username))
        if self.c.fetchone():
            return False, "อีเมลนี้ถูกใช้งานแล้ว"

        # อัปเดตตารางหลัก
        self.c.execute("UPDATE users SET username=?, email=?, profile_image=? WHERE username=?",
                    (new_username, new_email, new_profile_image, old_username))
        # อัปเดตตารางที่อ้างอิง username
        self.c.execute("UPDATE orders SET username=? WHERE username=?", (new_username, old_username))
        self.c.execute("UPDATE purchase_history SET username=? WHERE username=?", (new_username, old_username))
        self.conn.commit()
        return True, "บันทึกข้อมูลผู้ใช้เรียบร้อย"

    
    def email_in_use(self, email: str) -> bool:
        self.c.execute("SELECT 1 FROM users WHERE email=?", (email,))
        return self.c.fetchone() is not None

    def username_in_use(self, username: str) -> bool:
        self.c.execute("SELECT 1 FROM users WHERE username=?", (username,))
        return self.c.fetchone() is not None

    def register(self, username: str, password: str, email: str, profile_image: str | None = None):
        try:
            self.c.execute(
                "INSERT INTO users(username,password,email,profile_image) VALUES (?,?,?,?)",
                (username, password, email, profile_image)
            )
            self.conn.commit()
            return True, "สมัครสมาชิกสำเร็จ"
        except sqlite3.IntegrityError:
            return False, "Username นี้ถูกใช้แล้ว"

    def login(self, username: str, password: str):
        self.c.execute("SELECT password FROM users WHERE username=?", (username,))
        row = self.c.fetchone()
        if not row:
            return False, "ไม่พบบัญชีนี้"
        return (True, "เข้าสู่ระบบสำเร็จ") if row[0] == password else (False, "รหัสผ่านไม่ถูกต้อง")

    def match_user_email(self, username: str, email: str) -> bool:
        self.c.execute("SELECT 1 FROM users WHERE username=? AND email=?", (username, email))
        return self.c.fetchone() is not None

    def set_new_password(self, username: str, new_password: str):
        self.c.execute("UPDATE users SET password=? WHERE username=?", (new_password, username))
        self.conn.commit()
        return True, "ตั้งรหัสผ่านใหม่เรียบร้อย"

    # products
    def list_products(self):
        self.c.execute("SELECT id,name,price,stock,image_path FROM products ORDER BY id ASC")
        return self.c.fetchall()

    # ดึงข้อมูลสินค้า
    def get_product(self, product_id):
        self.c.execute("SELECT id,name,price,stock,image_path FROM products WHERE id=?", (product_id,))
        return self.c.fetchone()

    # เพิ่มสินค้าใหม่
    def add_product(self, name: str, price: int, stock: int, image_path: str|None):
        self.c.execute("INSERT INTO products(name,price,stock,image_path) VALUES (?,?,?,?)",
                       (name, int(price), int(stock), image_path))
        self.conn.commit()

    # อัปเดตสินค้า 
    def update_product(self, product_id: int, *, stock: int|None=None, price: int|None=None):
        if stock is not None:
            self.c.execute("UPDATE products SET stock=? WHERE id=?", (int(stock), product_id))
        if price is not None:
            self.c.execute("UPDATE products SET price=? WHERE id=?", (int(price), product_id))
        self.conn.commit()

    # ลบสินค้า 
    def delete_product(self, product_id: int):
        # ดึง path 
        self.c.execute("SELECT image_path FROM  products WHERE id=?", (product_id,))
        row = self.c.fetchone()
        img_path = row[0] if row else None

        # ลบสินค้า
        self.c.execute("DELETE FROM products WHERE  id=?", (product_id,))
        self.conn.commit()

        # ลบไฟล์รูป 
        try:
            if img_path and os.path.exists(img_path):
                os.remove(img_path)
        except Exception:
            pass

    # ดึงข้อมูลสินค้าทั้งหมด 
    def list_products_full(self):
        self.c.execute("SELECT id,name,price,stock,image_path FROM products ORDER BY id ASC")

        return self.c.fetchall()

    # อัปเดตสถานะคำสั่งซื้อ (ทำเสร็จแล้ว/ยังไม่เสร็จ)
    def mark_order_done(self, order_id: str, done: int = 1):
        self.c.execute("UPDATE orders SET is_done=? WHERE order_id=?", (int(done), order_id))
        self.conn.commit()

    # ดึงข้อมูลคำสั่งซื้อ (ใช้กับหน้า Orders)
    def list_orders(self, pending_only: bool = True):
        if pending_only:
            self.c.execute("""
                SELECT order_id, customer_name, phone, address, total, created_at, IFNULL(payment_image,''), IFNULL(is_done,0)
                FROM orders
                WHERE IFNULL(is_done,0)=0
                ORDER BY datetime(created_at) DESC, id DESC
            """)
        else:
            self.c.execute("""
                SELECT order_id, customer_name, phone, address, total, created_at, IFNULL(payment_image,''), IFNULL(is_done,0)
                FROM orders
                ORDER BY datetime(created_at) DESC, id DESC
            """)
        return self.c.fetchall()

    # ดึงข้อมูลคำสั่งซื้อทั้งหมด (ใช้กับหน้า All Orders)
    def list_orders_history(self):
        """
        ใช้แสดงหน้า All Orders — ดึงจาก orders + order_items โดยตรง
        คืนค่า: (order_id, username, created_at, payment_image, product_name, qty, sub_total)
        """
        self.c.execute("""
            SELECT o.order_id, o.username, o.created_at, IFNULL(o.payment_image,''),
                   i.product_name, i.qty, i.sub_total
            FROM orders o
            JOIN order_items i ON i.order_id = o.order_id
            ORDER BY datetime(o.created_at) DESC, o.id DESC, i.id ASC
        """)
        return self.c.fetchall()

    # สร้างรหัสคำสั่งซื้อแบบสุ่ม  และตรวจสอบความซ้ำซ้อนในฐานข้อมูล
    def generate_order_id(self):
        
        while True:
            code = f"TH{random.randint(1000,9999)}-{random.randint(10,99)}"
            self.c.execute("SELECT 1 FROM orders WHERE order_id=?", (code,))
            if not self.c.fetchone():
                return code
            

    # สร้างคำสั่งซื้อใหม่จากข้อมูลที่ได้รับมา และอัปเดตสต๊อกสินค้า + ประวัติการซื้อ
    def create_order(self, username, customer_name, phone, address, cart_items):
        """
        cart_items = list[(product_id, qty)]
        """
        order_id = self.generate_order_id()
        total = 0

        # คำนวณยอดรวม
        for pid, qty in cart_items:
            self.c.execute("SELECT name, price FROM products WHERE id=?", (pid,))
            row = self.c.fetchone()
            if not row:
                continue
            name, price = row
            total += int(price) * int(qty)

        # บันทึกหัวออเดอร์
        self.c.execute(
            "INSERT INTO orders(order_id, username, customer_name, phone, address, total) VALUES (?,?,?,?,?,?)",
            (order_id, username, customer_name, phone, address, int(total))
        )

        # บันทึกรายการย่อย + หักสต๊อก + เข้าประวัติ
        for pid, qty in cart_items:
            self.c.execute("SELECT name, price, stock FROM products WHERE id=?", (pid,))
            row = self.c.fetchone()
            if not row:
                continue
            name, price, stock = row
            sub = int(price) * int(qty)

            # order_items
            self.c.execute("""
                INSERT INTO order_items(order_id, product_id, product_name, qty, price_each, sub_total)
                VALUES (?,?,?,?,?,?)
            """, (order_id, pid, name, int(qty), int(price), sub))

            # stock
            self.c.execute("UPDATE products SET stock = MAX(stock - ?, 0) WHERE id=?", (int(qty), pid))

            # ---- purchase_history (ประวัติรายการ) ----
            self.c.execute("""
                INSERT INTO purchase_history(username, product_name, quantity, total_price)
                VALUES (?,?,?,?)
            """, (username, name, int(qty), sub))

        self.conn.commit()
        return order_id, total

    # ใช้กับหน้า All Order
    def list_purchase_history(self):
        self.c.execute("""
            SELECT username, product_name, quantity, total_price, timestamp
            FROM purchase_history
            ORDER BY timestamp DESC
        """)
        return self.c.fetchall()

    
    def get_order_items(self, order_id):
        self.c.execute("""
            SELECT product_name, qty, price_each, sub_total
            FROM order_items WHERE order_id=?
        """, (order_id,))
        return self.c.fetchall()

    def delete_order(self, order_id):
        self.c.execute("DELETE FROM order_items WHERE order_id=?", (order_id,))
        self.c.execute("DELETE FROM orders WHERE order_id=?", (order_id,))
        self.conn.commit()
        
    def list_orders(self):
        self.c.execute("""
            SELECT order_id, customer_name, phone, address, total, created_at, IFNULL(payment_image, '')
            FROM orders
            ORDER BY datetime(created_at) DESC, id DESC
        """)
        return self.c.fetchall()
    
    # ดึงข้อมูลตามช่วงวันที่ 
    def _orders_in_range(self, start_iso=None, end_iso=None):
        if start_iso and end_iso:
            self.c.execute("""
                SELECT order_id, total, created_at FROM orders
                WHERE datetime(created_at) >= datetime(?) AND datetime(created_at) < datetime(?)
            """, (start_iso, end_iso))
        else:
            self.c.execute("SELECT order_id, total, created_at FROM orders")
        return self.c.fetchall()
    
    def total_inventory_count(self) -> int:
        self.c.execute("SELECT COALESCE(SUM(stock),0) FROM products")
        r = self.c.fetchone()
        return int(r[0] or 0)



    def _items_sold_in_orders(self, order_ids):
        if not order_ids:
            return 0
        qmarks = ",".join("?"*len(order_ids))
        self.c.execute(f"SELECT COALESCE(SUM(qty),0) FROM order_items WHERE order_id IN ({qmarks})", tuple(order_ids))
        r = self.c.fetchone()
        return int(r[0] or 0)

    def sales_stats(self, start_iso=None, end_iso=None):
        rows = self._orders_in_range(start_iso, end_iso)
        order_ids = [r[0] for r in rows]
        revenue = sum(int(r[1] or 0) for r in rows)
        order_count = len(order_ids)
        items_sold = self._items_sold_in_orders(order_ids)
        return revenue, order_count, items_sold
    
    # ดึงข้อมูลผู้ใช้ (ใช้กับหน้า Profile)
    def get_user(self, username: str):
        self.c.execute("SELECT username, email, IFNULL(profile_image,'') FROM users WHERE username=?", (username,))
        return self.c.fetchone()

    def update_user_info(self, old_username: str, new_username: str, new_email: str, new_profile_path: str|None):
        # ตรวจ uniqueness
        if new_username != old_username:
            self.c.execute("SELECT 1 FROM users WHERE username=?", (new_username,))
            if self.c.fetchone():
                return False, "Username นี้ถูกใช้แล้ว"

        # อัปเดต users
        self.c.execute("""
            UPDATE users SET username=?, email=?, profile_image=COALESCE(?, profile_image)
            WHERE username=?""",
            (new_username, new_email, new_profile_path, old_username))

        # propagate ไปตารางที่อ้างอิง username
        if new_username != old_username:
            self.c.execute("UPDATE orders SET username=? WHERE username=?", (new_username, old_username))
            self.c.execute("UPDATE purchase_history SET username=? WHERE username=?", (new_username, old_username))

        self.conn.commit()
        return True, "บันทึกโปรไฟล์เรียบร้อย"

    def list_orders_by_user(self, username: str):
        self.c.execute("""
            SELECT order_id, customer_name, phone, address, total, created_at, IFNULL(payment_image,'')
            FROM orders
            WHERE username=?
            ORDER BY datetime(created_at) DESC, id DESC
        """, (username,))
        return self.c.fetchall()
    
    
    def get_top5_bestsellers(self):
        """
        คืนค่า: [(product_id, name, image_path, total_sold, price), ...]
        """
        self.c.execute("""
            SELECT 
                p.id,
                p.name,
                p.image_path,
                COALESCE(SUM(i.qty), 0) AS sold_qty,
                p.price
            FROM products p
            LEFT JOIN order_items i ON i.product_id = p.id
            GROUP BY p.id
            ORDER BY sold_qty DESC
            LIMIT 5
        """)
        return self.c.fetchall()


    

# ใบเสร็จ PDF
def _register_thai_font():
    P_REG = r"c:\USERS\SUPHI\APPDATA\LOCAL\MICROSOFT\WINDOWS\FONTS\THSARABUNNEW.TTF"
    P_BI  = r"c:\USERS\SUPHI\APPDATA\LOCAL\MICROSOFT\WINDOWS\FONTS\THSARABUNNEW BOLDITALIC.TTF"
    P_IT  = r"c:\USERS\SUPHI\APPDATA\LOCAL\MICROSOFT\WINDOWS\FONTS\THSARABUNNEW ITALIC.TTF"
    P_B   = r"c:\USERS\SUPHI\APPDATA\LOCAL\MICROSOFT\WINDOWS\FONTS\THSARABUNNEW BOLD.TTF"

    FAMILY = "THSarabunNew"

    # ลงทะเบียนไฟล์แต่ละน้ำหนัก/สไตล์
    pdfmetrics.registerFont(TTFont(FAMILY,      P_REG))
    pdfmetrics.registerFont(TTFont(FAMILY+"-B", P_B))
    pdfmetrics.registerFont(TTFont(FAMILY+"-I", P_IT))
    pdfmetrics.registerFont(TTFont(FAMILY+"-BI",P_BI))

    # map เป็น family (regular/bold/italic/bold-italic)
    addMapping(FAMILY, 0, 0, FAMILY)        # regular
    addMapping(FAMILY, 1, 0, FAMILY+"-B")   # bold
    addMapping(FAMILY, 0, 1, FAMILY+"-I")   # italic
    addMapping(FAMILY, 1, 1, FAMILY+"-BI")  # bold-italic

    return FAMILY

def make_receipt_pdf(app, order_id, save_dir=None):
    FAMILY = _register_thai_font()

    # เตรียมโฟลเดอร์บันทึกไฟล์ PDF
    if not save_dir:
        base = os.path.dirname(DB_PATH)
        save_dir = os.path.join(base, "receipts")
    os.makedirs(save_dir, exist_ok=True)
    pdf_path = os.path.join(save_dir, f"{order_id}.pdf")

    # ดึงข้อมูลคำสั่งซื้อ + รายการสินค้า
    app.db.c.execute("""
        SELECT customer_name, phone, address, total, created_at
        FROM orders WHERE order_id=?
    """, (order_id,))
    row = app.db.c.fetchone()
    if not row:
        raise RuntimeError("ไม่พบคำสั่งซื้อที่จะออกใบเสร็จ")
    customer_name, phone, address, total, created_at = row
    total = int(total or 0)
    items = app.db.get_order_items(order_id)  # [(name, qty, price_each, sub_total), ...]



    PW, A4H = A4  
    logo_h = 0
    logo_w_target = 210
    if getattr(app, "logo_path", None) and os.path.exists(app.logo_path):
        try:
            img = ImageReader(app.logo_path)
            iw, ih = img.getSize()
            logo_h = ih * (logo_w_target / float(iw))
        except Exception:
            logo_h = 0

    # ความสูงบล็อกข้อความหัวเรื่อง 
    header_text_h = (31 + 23 + 23 + 20 + 20 + 28 + 25 + 22) + 8 
    header_rule_h = 35
    table_header_h = 28
    row_h = 22
    after_table_rule_h = 12 + 30
    items_line_h = 30
    totals_h =  (22 + 33) + (27 + 38) + (22 + 30)  # Subtotal + Total + VAT 
    date_h   = 33
    bottom_rule_h = 55
    footer_h = 27 + 20  # ข้อความท้าย + เว้นระยะเล็กน้อย

    content_no_margin = (
        logo_h + header_text_h + header_rule_h +
        table_header_h + len(items) * row_h +
        after_table_rule_h + items_line_h +
        totals_h + date_h + bottom_rule_h + footer_h
    )

    PH = max(A4H, content_no_margin / 0.86)

    top_margin = PH * 0.93
    bottom_margin = PH * 0.07

    c = pdf_canvas.Canvas(pdf_path, pagesize=(PW, PH))

    # helper
    L, R = 40, PW - 40
    def T(x, y, text, size=19, bold=False):
        c.setFont(FAMILY + ("-B" if bold else ""), size)
        c.drawString(x, y, str(text))

    def TR(x, y, text, size=19, bold=False):
        c.setFont(FAMILY + ("-B" if bold else ""), size)
        c.drawRightString(x, y, str(text))

    def C(y, text, size=19, bold=False):
        c.setFont(FAMILY + ("-B" if bold else ""), size)
        c.drawCentredString(PW / 2, y, str(text))

    y = top_margin

    # โลโก้
    if getattr(app, "logo_path", None) and os.path.exists(app.logo_path):
        try:
            img = ImageReader(app.logo_path)
            iw, ih = img.getSize()
            tw = logo_w_target
            th = ih * (tw / float(iw))
            c.drawImage(img, (PW - tw)/2, y - th, width=tw, height=th, mask='auto')
            y -= th + 8
        except Exception:
            pass

    # หัวเรื่อง
    C(y, "สเตย์โซน", 31, True);                   y -= 31
    C(y, "บริษัท สเตย์โซน จำกัด", 21);             y -= 23
    C(y, "ตำบล,อำเภอ,จังหวัด ขอนแก่น", 21);       y -= 23
    C(y, "TAX ID: 010825032018", 19);              y -= 20
    C(y, "TEL: 095-968-0898", 19);                 y -= 25
    C(y, f"Order id: {order_id}", 21);             y -= 28
    C(y, "Receipt/TAX Invoice (ABB)", 23, True);   y -= 25
    C(y, "VAT Included", 21, True);                y -= 22

    # เส้นคั่นบนตาราง
    c.setDash(3, 3); c.line(L, y, R, y); c.setDash()
    y -= 35

    # คอลัมน์
    name_x  = L + 25
    qty_x   = PW * 0.55
    price_x = R - 5  # ชิดขวา

    T(name_x, y, "ชื่อสินค้า", 21)
    T(qty_x,  y, "จำนวนสินค้า", 21)
    TR(price_x, y, "ราคา", 21)
    y -= 28

    # รายการสินค้า
    for pname, qty, price_each, sub_total in items:
        T(name_x, y, str(pname), 19)
        T(qty_x,  y, f"{int(qty):,}", 19)
        TR(price_x, y, f"{int(sub_total):,} บาท", 19)
        y -= 22

    # เส้นคั่นหลังตาราง
    y -= 12
    c.setDash(3, 3); c.line(L, y, R, y); c.setDash()
    y -= 30

    # สรุปจำนวนชิ้น
    items_count = sum(int(q) for _, q, _, _ in items)
    T(L, y, "Items:", 21)
    TR(price_x, y, f"{items_count} ชิ้น", 21)
    y -= 30

    # รวมเงิน
    vat = round(total * 7 / 107)
    subtotal = total - vat

    T(L, y, "Subtotal:", 22); TR(price_x, y, f"{subtotal:,} บาท", 22); y -= 33
    T(L, y, "VAT 7% :", 22);  TR(price_x, y, f"{vat:,} บาท", 22);       y -= 30
    T(L, y, "Total:", 27, True); TR(price_x, y, f"{total:,} บาท", 27, True); y -= 38
    # วันที่
    try:
        date_str = str(created_at).split(" ")[0]
        ymd = date_str.split("-")
        disp = f"Date: {ymd[2]} -{ymd[1]}-{ymd[0]}" if len(ymd) == 3 else f"Date: {date_str}"
    except Exception:
        disp = "Date: -"
    T(L, y, disp, 21); y -= 33

    # เส้นคั่นก่อนท้ายใบเสร็จ
    c.setDash(3, 3); c.line(L, y, R, y); c.setDash()

    # ข้อความท้าย 
    footer_y = max(y - 55, bottom_margin + 60)
    C(footer_y, "Have a happyday day ;)", 27)

    c.showPage()
    c.save()
    return pdf_path










#กล่องกรอกข้อความ
def entry_box(master, placeholder: str, show_char=None):
    e = ct.CTkEntry(master, placeholder_text=placeholder,
                    fg_color=GRAY_LIGHT, border_color="#e0e0e0", border_width=1,
                    height=40, text_color="black", placeholder_text_color="#8a8a8a",
                    font=F(14))
    if show_char:
        e.configure(show=show_char)
    return e

#ปุ่มสีฟ้าอ่อน
def primary_btn(master, text, cmd):
    return ct.CTkButton(master, text=text, command=cmd,
                        fg_color=BLUE_LIGHT, hover_color=BLUE_DARK,
                        text_color="black", corner_radius=16, height=40,
                        font=F(14, "bold"))

#ปุ่มสีฟ้าเข้ม
def nav_btn(master, text, cmd, primary=False):
    return ct.CTkButton(master, text=text, command=cmd,
                        fg_color=BLUE_DARK if primary else BLUE_LIGHT,
                        hover_color=BLUE_DARK,
                        text_color="white" if primary else "black",
                        corner_radius=20, height=38,
                        font=F(14))

#ปุ่มสลับ Sign in / Sign up
def segmented(master, on_switch):
    return ct.CTkSegmentedButton(
        master, values=["Sign in", "Sign up"],
        fg_color=GRAY_LIGHT,
        selected_color=BLUE_LIGHT, selected_hover_color=BLUE_DARK,
        unselected_color=GRAY_LIGHT, unselected_hover_color="#ececec",
        text_color="black",
        command=lambda v: on_switch(v),
        font=F(14, "bold")
    )
    
#วางฟอร์ม sign in / up 
def half_form(parent, top_offset=0.30):
    box = ct.CTkFrame(parent, fg_color=WHITE)
    box.place(relx=0.5, rely=top_offset, relwidth=0.5, anchor="n")
    box.grid_columnconfigure(0, weight=1)
    return box

class UserProfilePage(ct.CTkFrame):
    
    CARD_RELWIDTH = 0.60
    CARD_RELY     = 0.22
    CARD_HEIGHT   = 560   

    USERNAME_RE = re.compile(r'^[A-Za-z][A-Za-z0-9._-]{5,}$')   # เริ่มด้วยตัวอักษร, ≥6 ตัว
    EMAIL_RE    = re.compile(r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')

    def __init__(self, master, app):
        super().__init__(master, fg_color=WHITE)
        self.app = app
        self.editing = False
        self._picked_profile = None
        self._cur_profile_path = None
        self._cur_email = ""
        self._cur_username = ""

        self.grid_columnconfigure(0, weight=1)
        self.topbar = TopBar(self, app)
        self.topbar.grid(row=0, column=0, sticky="ew")

        # ===== การ์ดโปรไฟล์ =====
        self.card = ct.CTkFrame(
            self, fg_color=WHITE, corner_radius=20,
            border_width=1, border_color="#eeeeee"
        )
        self.card.place(relx=0.5, rely=self.CARD_RELY, anchor="n", relwidth=self.CARD_RELWIDTH)
        self.card.configure(height=self.CARD_HEIGHT)
        self.card.grid_columnconfigure(0, weight=1)
        self.card.grid_propagate(False)

        # รูปโปรไฟล์ 
        self._avatar_holder = ct.CTkFrame(self.card, fg_color=WHITE)
        self._avatar_holder.grid(row=0, column=0, pady=(30, 16))
        self._big_avatar_size = 180

        # ปุ่มอัปโหลดรูป
        self._upload_btn = ct.CTkButton(
            self.card, text="อัปโหลดรูปภาพ", width=160, height=34,
            fg_color=GRAY_LIGHT, hover_color=GRAY_DARK, text_color="black",
            font=F(14), command=self._pick_image
        )
        self._upload_btn.grid(row=1, column=0, pady=(0, 10))

        # spacer แทนตำแหน่งปุ่มอัปโหลด
        self._upload_spacer = ct.CTkFrame(self.card, fg_color=WHITE, height=34)
        self._upload_spacer.grid(row=1, column=0, pady=(0, 10), sticky="n")
        self._upload_spacer.grid_propagate(False)

        self._upload_btn.grid_remove()
        self._upload_spacer.grid()

        # ข้อมูลผู้ใช้ 
        self._name_lbl = ct.CTkLabel(self.card, text="User", font=F(34, "bold"), text_color="black")
        self._name_lbl.grid(row=2, column=0, pady=(0, 6))

        self._name_entry = entry_box(self.card, "username")
        self._name_entry.configure(height=42, width=360, font=F(16))
        self._name_entry.grid(row=2, column=0, pady=(0, 6))
        self._name_entry.grid_remove()

        # Email
        self._email_row = ct.CTkFrame(self.card, fg_color=WHITE)
        self._email_row.grid(row=3, column=0, pady=(0, 20))
        ct.CTkLabel(self._email_row, text="Email :", font=F(18), text_color="black").pack(side="left", padx=(0, 8))
        self._email_val = ct.CTkLabel(self._email_row, text="-", font=F(18), text_color="black")
        self._email_val.pack(side="left")

        self._email_edit_row = ct.CTkFrame(self.card, fg_color=WHITE)
        self._email_edit_row.grid(row=3, column=0, pady=(0, 20))
        ct.CTkLabel(self._email_edit_row, text="Email :", font=F(18), text_color="black").pack(side="left", padx=(0, 8))
        self._email_entry = entry_box(self._email_edit_row, "you@email.com")
        self._email_entry.configure(width=360)
        self._email_entry.pack(side="left")
        self._email_edit_row.grid_remove()

        # ปุ่มบันทึก / ยกเลิก
        btns = ct.CTkFrame(self.card, fg_color=WHITE, height=44)
        btns.grid(row=4, column=0, pady=(4, 10))
        btns.grid_propagate(False)

        self._save_btn = ct.CTkButton(btns, text="บันทึก", width=140, height=36,
                                      fg_color=GRAY_LIGHT, hover_color=GRAY_DARK, text_color="black",
                                      corner_radius=18, font=F(14), command=self._save)
        self._cancel_btn = ct.CTkButton(btns, text="ยกเลิก", width=120, height=36,
                                        fg_color=WHITE, hover_color="#f0f0f0", text_color="black",
                                        corner_radius=18, font=F(14), command=self._toggle_edit)
        self._save_btn.pack_forget()
        self._cancel_btn.pack_forget()

        self._edit_btn = ct.CTkButton(
            self.card, text="แก้ไขข้อมูล", width=150, height=36, corner_radius=18,
            fg_color=GRAY_LIGHT, hover_color=GRAY_DARK, text_color="black",
            command=self._toggle_edit, font=F(14)
        )
        self._edit_btn.grid(row=5, column=0, pady=(10, 8))

        ct.CTkButton(
            self.card, text="Log out", width=170, height=40, corner_radius=18,
            fg_color=BLUE_LIGHT, hover_color=BLUE_DARK, text_color="black",
            command=self.app.logout, font=F(16, "bold")
        ).grid(row=6, column=0, pady=(4, 30))

        self._history_btn = ct.CTkButton(
            self, text="Order History", width=240, height=40,
            corner_radius=18, fg_color=BLUE_LIGHT, hover_color=BLUE_DARK, text_color="black",
            command=lambda: self.app.show("UserOrders"), font=F(14, "bold")
        )
        self._history_btn.place(in_=self.card, relx=0.5, rely=1.0, y=12, anchor="n")

        self.refresh()


    def _render_avatar(self, path):
        for w in self._avatar_holder.winfo_children():
            w.destroy()
        try:
            im = make_ctk_circle_image(path, size=self._big_avatar_size)
            lbl = ct.CTkLabel(self._avatar_holder, text="", image=im)
            lbl.image = im
            lbl.pack()
        except Exception:
            pass

    def _toggle_edit(self):
        self.editing = not self.editing
        if self.editing:
            self._upload_spacer.grid_remove()
            self._upload_btn.grid()
            self._name_lbl.grid_remove()
            self._name_entry.grid()
            self._email_row.grid_remove()
            self._email_edit_row.grid()
            self._edit_btn.grid_remove()
            self._save_btn.pack(side="left", padx=6)
            self._cancel_btn.pack(side="left", padx=6)
        else:
            self._upload_btn.grid_remove()
            self._upload_spacer.grid()
            self._name_entry.grid_remove()
            self._name_lbl.grid()
            self._email_edit_row.grid_remove()
            self._email_row.grid()
            self._edit_btn.grid(row=5, column=0, pady=(10, 8))
            self._save_btn.pack_forget()
            self._cancel_btn.pack_forget()
            self._picked_profile = None

    def _pick_image(self):
        p = filedialog.askopenfilename(
            title="เลือกรูปโปรไฟล์",
            filetypes=[("รูปภาพ", "*.png;*.jpg;*.jpeg;*.webp;*.bmp")]
        )
        if not p:
            return
        self._picked_profile = p
        self._render_avatar(p)

    def _save(self):
        old_u = self._cur_username
        new_u = self._name_entry.get().strip()
        new_email = self._email_entry.get().strip()

        if not new_u or not new_email:
            messagebox.showwarning("โปรไฟล์", "กรอกชื่อผู้ใช้และอีเมลให้ครบ")
            return

        # ตรวจชื่อผู้ใช้
        if not self.USERNAME_RE.match(new_u):
            messagebox.showwarning(
                "โปรไฟล์",
                "ชื่อผู้ใช้ต้องเป็นภาษาอังกฤษเท่านั้น\n"
                "- เริ่มด้วยตัวอักษร (A–Z หรือ a–z)\n"
                "- ยาวอย่างน้อย 6 ตัวอักษร\n"
                "- อนุญาตเฉพาะ A–Z, a–z, 0–9, ., _, -"
            )
            return

        # ตรวจอีเมล
        if not self.EMAIL_RE.match(new_email):
            messagebox.showwarning("โปรไฟล์", "รูปแบบอีเมลไม่ถูกต้อง")
            return

        # บันทึกภาพ
        save_profile = self._cur_profile_path
        if self._picked_profile:
            try:
                profiles_dir = os.path.join(os.path.dirname(DB_PATH), "profiles")
                os.makedirs(profiles_dir, exist_ok=True)
                ext = os.path.splitext(self._picked_profile)[1].lower() or ".png"
                save_profile = os.path.join(profiles_dir, f"{new_u}{ext}")
                Image.open(self._picked_profile).save(save_profile)
            except Exception:
                pass

        ok, msg = self.app.db.update_user_profile(old_u, new_u, new_email, save_profile)
        if not ok:
            messagebox.showerror("โปรไฟล์", msg)
            return

        self.app.current_user = new_u
        messagebox.showinfo("โปรไฟล์", msg)
        self.refresh()
        self._toggle_edit()
        try:
            self.topbar.refresh_avatar()
        except Exception:
            pass

    def refresh(self):
        row = self.app.get_current_user_info()
        if row:
            uname, email, pimg = row
        else:
            uname, email, pimg = ("User", "-", None)

        self._cur_username = uname or "User"
        self._cur_email = email or "-"
        self._cur_profile_path = pimg

        self._name_lbl.configure(text=self._cur_username)
        self._email_val.configure(text=self._cur_email)
        self._name_entry.delete(0, tk.END)
        self._name_entry.insert(0, self._cur_username)
        self._email_entry.delete(0, tk.END)
        self._email_entry.insert(0, self._cur_email)
        self._render_avatar(self._cur_profile_path or getattr(self.app, "app_image_path", None))

        if self.editing:
            self._toggle_edit()




class UserOrders(ct.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color=WHITE)
        self.app = app
        self.grid_columnconfigure(0, weight=1)

        self.topbar = TopBar(self, app)
        self.topbar.grid(row=0, column=0, sticky="ew")

        ct.CTkButton(self, text="Back", width=100, height=36,
                     fg_color=BLUE_LIGHT, hover_color=BLUE_DARK, text_color="black",
                     command=lambda: self.app.show("UserProfile"), font=F(14))\
            .grid(row=1, column=0, sticky="w", padx=50, pady=(8,0))

        self.body = ct.CTkScrollableFrame(self, fg_color=WHITE)
        self.body.grid(row=2, column=0, sticky="nsew", padx=40, pady=10)

    def refresh(self):
        for w in self.body.winfo_children():
            w.destroy()
        try:
            self.topbar.refresh_avatar()
        except Exception:
            pass

        u = getattr(self.app, "current_user", None)
        if not u:
            ct.CTkLabel(self.body, text="ยังไม่ได้ล็อกอิน", font=F(18)).pack(pady=20)
            return

        # ดึงออเดอร์ของผู้ใช้
        self.app.db.c.execute("""
            SELECT order_id, customer_name, phone, address, total, created_at
            FROM orders WHERE username=? ORDER BY datetime(created_at) DESC
        """, (u,))
        orders = self.app.db.c.fetchall()
        if not orders:
            ct.CTkLabel(self.body, text="ยังไม่มีประวัติคำสั่งซื้อ", font=F(18)).pack(pady=20)
            return

        for (oid, cname, phone, addr, total, created_at) in orders:
            card = ct.CTkFrame(self.body, fg_color=WHITE, corner_radius=16,
                               border_width=1, border_color="#e5e5e5")
            card.pack(fill="x", padx=10, pady=10)

            ct.CTkLabel(card, text=f"ORDER ID: {oid}", font=F(22, "bold"), text_color="black")\
                .pack(anchor="w", padx=14, pady=(12, 4))
            ct.CTkLabel(card, text=f"ชื่อ: {cname}\nเบอร์โทร: {phone}\nที่อยู่: {addr}",
                        font=F(16), text_color="black", justify="left").pack(anchor="w", padx=14)

            # รายการสินค้าในออเดอร์นี้
            tbl = ct.CTkFrame(card, fg_color=WHITE); tbl.pack(fill="x", padx=12, pady=(8,6))
            tbl.grid_columnconfigure(0, weight=4); tbl.grid_columnconfigure(1, weight=1)
            ct.CTkLabel(tbl, text="ชื่อสินค้า", font=F(16, "bold")).grid(row=0, column=0, sticky="w")
            ct.CTkLabel(tbl, text="จำนวนที่สั่ง", font=F(16, "bold")).grid(row=0, column=1, sticky="e")
            r = 1
            for pname, qty, price_each, sub_total in self.app.db.get_order_items(oid):
                ct.CTkLabel(tbl, text=pname, font=F(16)).grid(row=r, column=0, sticky="w")
                ct.CTkLabel(tbl, text=str(qty), font=F(16)).grid(row=r, column=1, sticky="e")
                r += 1

            ct.CTkLabel(card, text=f"ราคารวมทั้งหมด: {int(total):,} บาท",
                        font=F(18, "bold"), text_color="black").pack(anchor="e", padx=14, pady=(0,10))

            # ปุ่มเปิดใบเสร็จ
            def _open(oid=oid):
                base = os.path.join(os.path.dirname(DB_PATH), "receipts")
                pdf_path = os.path.join(base, f"{oid}.pdf")
                if os.path.exists(pdf_path):
                    open_file_auto(pdf_path)
                else:
                    messagebox.showwarning("Receipt", "ยังไม่พบไฟล์ใบเสร็จสำหรับคำสั่งซื้อนี้")
            ct.CTkButton(card, text="Open Receipt", width=160, height=36,
                         fg_color=BLUE_LIGHT, hover_color=BLUE_DARK, text_color="black",
                         command=_open, font=F(14)).pack(pady=(0, 14))



# สินค้าในประวัติการสั่งซื้อของผู้ใช้
class UserOrdersPage(ct.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color=WHITE)
        self.app = app
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

        TopBar(self, app).grid(row=0, column=0, sticky="ew")

        # ปุ่ม Back
        ct.CTkButton(self, text="Back", width=100, height=36,
                     fg_color=BLUE_LIGHT, hover_color=BLUE_DARK, text_color="black",
                     corner_radius=18, command=lambda: self.app.show("UserProfile"))\
            .grid(row=1, column=0, sticky="w", padx=50, pady=(8, 0))

        ct.CTkLabel(self, text="Order History", font=F(36, "bold"),
                    text_color="black").grid(row=1, column=0, pady=(8,0))

        self.body = ct.CTkScrollableFrame(self, fg_color=WHITE)
        self.body.grid(row=2, column=0, sticky="nsew", padx=40, pady=10)
        hide_scrollbar(self.body)

    def refresh(self):
        for w in self.body.winfo_children(): w.destroy()
        u = self.app.current_user
        if not u:
            ct.CTkLabel(self.body, text="กรุณาเข้าสู่ระบบ", font=F(18), text_color="black").pack(pady=20)
            return
        
        # ดึงออเดอร์ของผู้ใช้
        self.app.db.c.execute("""
            SELECT order_id, customer_name, phone, address, total, created_at, IFNULL(payment_image,'')
            FROM orders WHERE username=? ORDER BY datetime(created_at) DESC, id DESC
        """, (u,))
        orders = self.app.db.c.fetchall()
        if not orders:
            ct.CTkLabel(self.body, text="ยังไม่มีประวัติการสั่งซื้อ", font=F(18), text_color="black").pack(pady=20)
            return

        for (oid, cname, phone, addr, total, created_at, pay_img) in orders:
            card = ct.CTkFrame(self.body, fg_color=WHITE, corner_radius=18,
                               border_width=1, border_color="#dedede")
            card.pack(fill="x", padx=10, pady=12)

            inner = ct.CTkFrame(card, fg_color=WHITE)
            inner.pack(fill="both", padx=22, pady=20)

            head = ct.CTkFrame(inner, fg_color=GRAY_LIGHT, corner_radius=20)
            head.pack(anchor="w", pady=(0, 10))
            ct.CTkLabel(head, text=f"ORDER ID:  {oid}", font=F(24, "bold"),
                        text_color="black").pack(padx=16, pady=8)

            info = ct.CTkFrame(inner, fg_color=WHITE); info.pack(anchor="w", pady=(6, 10))
            ct.CTkLabel(info, text=f"ชื่อ :  {cname}", font=F(15)).grid(row=0, column=0, sticky="w")
            ct.CTkLabel(info, text=f"เบอร์โทร :  {phone}", font=F(15)).grid(row=1, column=0, sticky="w")
            ct.CTkLabel(info, text=f"ที่อยู่ :  {addr}", font=F(15)).grid(row=2, column=0, sticky="w")

            # ตารางสินค้า
            ct.CTkLabel(inner, text="คำสั่งซื้อ", font=F(20, "bold")).pack(anchor="w", pady=(10,6))
            table = ct.CTkFrame(inner, fg_color=WHITE); table.pack(fill="x")
            table.grid_columnconfigure(0, weight=4)
            table.grid_columnconfigure(1, weight=1)
            table.grid_columnconfigure(2, weight=1)
            hdrf = F(16, "bold")
            ct.CTkLabel(table, text="ชื่อสินค้า", font=hdrf).grid(row=0, column=0, sticky="w")
            ct.CTkLabel(table, text="จำนวนที่สั่ง", font=hdrf).grid(row=0, column=1, sticky="e")
            ct.CTkLabel(table, text="ราคา", font=hdrf).grid(row=0, column=2, sticky="e")
            ct.CTkFrame(table, height=1, fg_color="#e5e5e5")\
                .grid(row=1, column=0, columnspan=3, sticky="ew", pady=(7,9))

            r = 2
            for pname, qty, price_each, sub_total in self.app.db.get_order_items(oid):
                ct.CTkLabel(table, text=pname, font=F(16)).grid(row=r, column=0, sticky="w", pady=3)
                ct.CTkLabel(table, text=str(qty), font=F(16)).grid(row=r, column=1, sticky="e", pady=3)
                ct.CTkLabel(table, text=f"{sub_total:,} บาท", font=F(16)).grid(row=r, column=2, sticky="e", pady=3)
                r += 1

            ct.CTkFrame(table, height=1, fg_color="#e5e5e5")\
                .grid(row=r, column=0, columnspan=3, sticky="ew", pady=(9,9))
            r += 1
            ct.CTkLabel(table, text="ราคารวมทั้งหมด", font=F(18, "bold")).grid(row=r, column=1, sticky="e")
            ct.CTkLabel(table, text=f"{int(total):,} บาท", font=F(18, "bold")).grid(row=r, column=2, sticky="e")

            # ปุ่ม Open Receipt
            def _open(oid=oid):
                base = os.path.dirname(DB_PATH)
                pdf_path = os.path.join(base, "receipts", f"{oid}.pdf")
                if os.path.exists(pdf_path):
                    open_file_auto(pdf_path)
                else:
                    messagebox.showwarning("Receipt", "ยังไม่พบไฟล์ใบเสร็จของคำสั่งซื้อนี้")
            ct.CTkButton(inner, text="Open Receipt", width=160, height=36,
                         fg_color=BLUE_LIGHT, hover_color=BLUE_DARK,
                         text_color="black", corner_radius=18, command=_open)\
                .pack(pady=(14, 0))



#เข้าสู่ระบบ
class SignInPage(ct.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color=WHITE)
        self.app = app
        self.grid_columnconfigure((0,1), weight=1, uniform="half")
        self.grid_rowconfigure(0, weight=1)

        LeftImage(self, app.left_image_path).grid(row=0, column=0, sticky="nsew")
        right = ct.CTkFrame(self, fg_color=WHITE)
        right.grid(row=0, column=1, sticky="nsew", padx=60, pady=40)
        right.grid_columnconfigure(0, weight=1)

        ct.CTkLabel(right, text="Hello!", font=F(36, "bold"),
                    text_color="black").grid(row=0, column=0, pady=(160, 8))

        # ปุ่มสลับไป Sign up
        seg = segmented(right, on_switch=lambda v: self.app.show("SignUp") if v=="Sign up" else None)
        seg.set("Sign in")
        seg.grid(row=1, column=0, pady=(0, 50), sticky="n")

        # ฟอร์มเข้าสู่ระบบ
        form = half_form(right, top_offset=0.38)
        ct.CTkLabel(form, text="Username", font=F(14), text_color="black", anchor="w")\
            .grid(row=0, column=0, sticky="w")
        self.username = entry_box(form, "Enter your username")
        self.username.grid(row=1, column=0, pady=(0,8), sticky="ew")

        ct.CTkLabel(form, text="Password", font=F(14), text_color="black", anchor="w")\
            .grid(row=2, column=0, sticky="w")

        # ช่องรหัสผ่าน
        pw_frame = ct.CTkFrame(form, fg_color=WHITE)
        pw_frame.grid(row=3, column=0, pady=(0,8), sticky="ew")
        pw_frame.grid_columnconfigure(0, weight=1)

        self.password = entry_box(pw_frame, "Enter your password", show_char="•")
        self.password.grid(row=0, column=0, sticky="ew")

        self.show_pw = tk.BooleanVar(value=False)
        ct.CTkButton(
            pw_frame, text="ㆅ", width=40, fg_color=GRAY_LIGHT, hover_color=GRAY_DARK,
            command=lambda: self.toggle_pw(self.password, self.show_pw),
            text_color="black", font=F(14)
        ).grid(row=0, column=1, padx=(6,0))

        # ปุ่มลืมรหัสผ่าน
        ct.CTkButton(form, text="Forgot password?", fg_color="transparent", hover=False,
                     text_color=BLUE_DARK, command=lambda: self.app.show("ResetRequest"), font=F(13))\
            .grid(row=4, column=0, sticky="e", pady=(0,6))

        # ปุ่ม Sign in
        primary_btn(form, "Login", self.do_login).grid(row=5, column=0, sticky="ew", pady=(6,8))

    def toggle_pw(self, entry, var):
        """สลับการแสดง/ซ่อนรหัสผ่าน"""
        var.set(not var.get())
        entry.configure(show="" if var.get() else "•")

    # ฟังก์ชันเข้าสู่ระบบ
    def do_login(self):
        u, p = self.username.get().strip(), self.password.get()
        if not u or not p:
            messagebox.showwarning("Login", "กรอกข้อมูลให้ครบ"); return

        # ตรวจสอบ Admin
        if u == "yokyak" and p == "yokyak08":
            messagebox.showinfo("Login", "ยินดีต้อนรับ Admin!")
            self.app.current_user = u
            self.app.is_admin = True
            self.app.show("AdminDashboard")
            return

        ok, msg = self.app.db.login(u, p)
        if not ok:
            messagebox.showerror("Login", msg); return

        messagebox.showinfo("Login", msg)
        self.app.current_user = u
        self.app.is_admin = False
        self.app.show("Home")

    # reset form
    def reset(self):
        try:
            self.username.delete(0, tk.END)
            self.password.delete(0, tk.END)
        except Exception:
            pass



#sign up  สมัคร
class SignUpPage(ct.CTkFrame):
    # รูปแบบการตรวจสอบชื่อผู้ใช้และอีเมล 
    USERNAME_RE = re.compile(r'^[A-Za-z][A-Za-z0-9._-]{5,}$')                   
    EMAIL_RE    = re.compile(r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')
    ASCII_RE    = re.compile(r'^[\x20-\x7E]+$')

    def __init__(self, master, app):
        super().__init__(master, fg_color=WHITE)
        self.app = app
        self.grid_columnconfigure((0, 1), weight=1, uniform="half")
        self.grid_rowconfigure(0, weight=1)

        LeftImage(self, app.left_image_path).grid(row=0, column=0, sticky="nsew")
        
        right = ct.CTkFrame(self, fg_color=WHITE)
        right.grid(row=0, column=1, sticky="nsew", padx=60, pady=40)
        right.grid_columnconfigure(0, weight=1)

        ct.CTkLabel(right, text="Hello!", font=F(36, "bold"),
                    text_color="black").grid(row=0, column=0, pady=(60, 8))
        seg = segmented(right, on_switch=lambda v: self.app.show("SignIn") if v == "Sign in" else None)
        seg.set("Sign up")
        seg.grid(row=1, column=0, pady=(0, 24), sticky="n")

        # อัปโหลดโปรไฟล์
        AVATAR = 160
        self.profile_path = None
        self._preview_imgtk = None

        avatar_wrap = ct.CTkFrame(right, fg_color=WHITE)
        avatar_wrap.grid(row=2, column=0, sticky="n", pady=(6, 10))
        avatar_wrap.grid_columnconfigure(0, weight=1)

        self.avatar_holder = tk.Label(avatar_wrap, bg=WHITE, bd=0, highlightthickness=0)
        self.avatar_holder.grid(row=0, column=0, pady=(0, 6))

        ph = Image.new("RGBA", (AVATAR, AVATAR), (0, 0, 0, 0))
        ImageDraw.Draw(ph).ellipse((0, 0, AVATAR-1, AVATAR-1), fill=(235, 235, 235, 255))
        self._preview_imgtk = ImageTk.PhotoImage(ph)
        self.avatar_holder.configure(image=self._preview_imgtk, text="ยังไม่มี\nรูปภาพ",
                                     compound="center", fg="#666666")
        self.avatar_holder.image = self._preview_imgtk

        ct.CTkLabel(avatar_wrap, text="Profile", text_color="black", font=F(14))\
            .grid(row=1, column=0, pady=(0, 2))
        ct.CTkButton(
            avatar_wrap, text="อัปโหลดรูปภาพ",
            fg_color=GRAY_LIGHT, hover_color=GRAY_DARK, text_color="black",
            command=self._pick_profile, font=F(14)
        ).grid(row=2, column=0)

        # ฟอร์มสมัคร
        ENTRY_W = 360
        form = ct.CTkFrame(right, fg_color=WHITE)
        form.grid(row=3, column=0, sticky="n", pady=(6, 0))
        form.grid_columnconfigure(0, weight=1)

        ct.CTkLabel(form, text="Username", font=F(14), text_color="black", anchor="w")\
            .grid(row=0, column=0, sticky="w")
        self.username = entry_box(form, "อย่างน้อย 6 ตัวอักษร"); self.username.configure(width=ENTRY_W)
        self.username.grid(row=1, column=0, pady=(0,8), sticky="w")

        ct.CTkLabel(form, text="Email", font=F(14), text_color="black", anchor="w")\
            .grid(row=2, column=0, sticky="w")
        self.email = entry_box(form, "your@email.com"); self.email.configure(width=ENTRY_W)
        self.email.grid(row=3, column=0, pady=(0,8), sticky="w")

        # password
        ct.CTkLabel(form, text="Password", font=F(14), text_color="black", anchor="w")\
            .grid(row=4, column=0, sticky="w")
        pw_frame = ct.CTkFrame(form, fg_color=WHITE)
        pw_frame.grid(row=5, column=0, sticky="w", pady=(0,8))
        pw_frame.grid_columnconfigure(0, weight=1)
        self.password = entry_box(pw_frame, "อย่างน้อย 8 ตัวอักษร", show_char="•"); self.password.configure(width=ENTRY_W)
        self.password.grid(row=0, column=0, sticky="ew")
        self.show_pw_signup = tk.BooleanVar(value=False)
        ct.CTkButton(pw_frame, text="ㆅ", width=40, fg_color=GRAY_LIGHT, hover_color=GRAY_DARK,
                     text_color="black", font=F(14),
                     command=lambda: self.toggle_pw(self.password, self.show_pw_signup))\
            .grid(row=0, column=1, padx=(6,0))

        # Confirm Password 
        ct.CTkLabel(form, text="Confirm Password", font=F(14), text_color="black", anchor="w")\
            .grid(row=6, column=0, sticky="w")
        cpw_frame = ct.CTkFrame(form, fg_color=WHITE)
        cpw_frame.grid(row=7, column=0, sticky="w", pady=(0,10))
        cpw_frame.grid_columnconfigure(0, weight=1)
        self.cpassword = entry_box(cpw_frame, "พิมพ์รหัสผ่านอีกครั้ง", show_char="•"); self.cpassword.configure(width=ENTRY_W)
        self.cpassword.grid(row=0, column=0, sticky="ew")
        self.show_cpw_signup = tk.BooleanVar(value=False)
        ct.CTkButton(cpw_frame, text="ㆅ", width=40, fg_color=GRAY_LIGHT, hover_color=GRAY_DARK,
                     text_color="black", font=F(14),
                     command=lambda: self.toggle_pw(self.cpassword, self.show_cpw_signup))\
            .grid(row=0, column=1, padx=(6,0))

        # ปุ่มสมัคร
        btn_signup = primary_btn(form, "Sign Up", self.do_register)
        btn_signup.configure(width=ENTRY_W, height=44, corner_radius=18)
        btn_signup.grid(row=8, column=0, pady=(10, 8), sticky="w")

    def toggle_pw(self, entry, var):
        var.set(not var.get())
        entry.configure(show="" if var.get() else "•")

    def do_register(self):
        u, email, pw, cpw = (
            self.username.get().strip(),
            self.email.get().strip(),
            self.password.get(),
            self.cpassword.get(),
        )

        # ต้องกรอกครบทุกช่อง
        if not u or not email or not pw or not cpw:
            messagebox.showwarning("Register", "กรุณากรอกข้อมูลให้ครบทุกช่องก่อนสมัคร")
            return

        # ต้องอัปโหลดรูปโปรไฟล์ด้วย
        if not self.profile_path:
            messagebox.showwarning("Register", "กรุณาอัปโหลดรูปโปรไฟล์ก่อนสมัคร")
            return

        # ตรวจอังกฤษเท่านั้นสำหรับ Username
        if not self.USERNAME_RE.match(u):
            messagebox.showwarning(
                "Register",
                "Username ต้องใช้ภาษาอังกฤษเท่านั้น\n"
                "- เริ่มด้วยตัวอักษร (A–Z หรือ a–z)\n"
                "- ยาวอย่างน้อย 6 ตัวอักษร\n"
                "- ใช้ได้เฉพาะ A–Z, a–z, 0–9, จุด (.), ขีดล่าง (_), ขีดกลาง (-)"
            )
            return

        # 
        if not self.EMAIL_RE.match(email):
            messagebox.showwarning("Register", "รูปแบบอีเมลไม่ถูกต้อง (ใช้ตัวอักษรภาษาอังกฤษเท่านั้น)")
            return

        # 
        if not self.ASCII_RE.match(pw):
            messagebox.showwarning("Register", "Password ต้องเป็นอักขระภาษาอังกฤษ/ตัวเลข/สัญลักษณ์มาตรฐานเท่านั้น (ASCII)")
            return

        # เงื่อนไข
        if len(pw) < 8:
            messagebox.showwarning("Register", "Password อย่างน้อย 8 ตัวอักษร")
            return
        if not re.search(r'[A-Z]', pw):
            messagebox.showwarning("Register", "Password ต้องมีตัวพิมพ์ใหญ่ อย่างน้อย 1 ตัว")
            return
        if not re.search(r'[0-9]', pw):
            messagebox.showwarning("Register", "Password ต้องมีตัวเลข อย่างน้อย 1 ตัว")
            return
        if pw != cpw:
            messagebox.showwarning("Register", "รหัสผ่านไม่ตรงกัน")
            return

        # ตรวจซ้ำในระบบ
        if self.app.db.username_in_use(u):
            messagebox.showerror("Register", "Username นี้ถูกใช้แล้ว")
            return
        if self.app.db.email_in_use(email):
            messagebox.showerror("Register", "อีเมลนี้ถูกใช้งานแล้ว")
            return

        # เซฟไฟล์โปรไฟล์
        save_path = None
        try:
            profiles_dir = os.path.join(os.path.dirname(DB_PATH), "profiles")
            os.makedirs(profiles_dir, exist_ok=True)
            ext = os.path.splitext(self.profile_path)[1].lower() or ".png"
            save_path = os.path.join(profiles_dir, f"{u}{ext}")
            Image.open(self.profile_path).save(save_path)
        except Exception:
            save_path = None

        ok, msg = self.app.db.register(u, pw, email, save_path)
        messagebox.showinfo("Register", msg)
        if ok:
            self.app.show("SignIn")

    # เลือกรูปโปรไฟล์
    def _pick_profile(self):
        AVATAR = 160
        path = filedialog.askopenfilename(
            title="เลือกรูปโปรไฟล์",
            filetypes=[("รูปภาพ", "*.png;*.jpg;*.jpeg;*.webp;*.bmp")],
        )
        if not path:
            return
        self.profile_path = path
        try:
            img = Image.open(path).convert("RGBA")
            img = ImageOps.fit(img, (AVATAR, AVATAR), Image.LANCZOS)
            mask = Image.new("L", (AVATAR, AVATAR), 0)
            ImageDraw.Draw(mask).ellipse((0, 0, AVATAR-1, AVATAR-1), fill=255)
            img.putalpha(mask)
            self._preview_imgtk = ImageTk.PhotoImage(img)
            self.avatar_holder.configure(image=self._preview_imgtk, text="")
            self.avatar_holder.image = self._preview_imgtk
        except Exception:
            messagebox.showerror("รูปภาพ", "ไม่สามารถโหลดรูปนี้ได้")

    # reset form
    def reset(self):
        try:
            self.username.delete(0, tk.END)
            self.email.delete(0, tk.END)
            self.password.delete(0, tk.END)
            self.cpassword.delete(0, tk.END)
        except Exception:
            pass

        self.profile_path = None
        AVATAR = 160
        ph = Image.new("RGBA", (AVATAR, AVATAR), (0, 0, 0, 0))
        ImageDraw.Draw(ph).ellipse((0, 0, AVATAR-1, AVATAR-1), fill=(235, 235, 235, 255))
        self._preview_imgtk = ImageTk.PhotoImage(ph)
        self.avatar_holder.configure(image=self._preview_imgtk, text="ยังไม่มี\nรูปภาพ")
        self.avatar_holder.image = self._preview_imgtk

# ลืมรหัสผ่าน 
class ResetRequestPage(ct.CTkFrame):
    USERNAME_RE = re.compile(r'^[A-Za-z][A-Za-z0-9._-]{5,}$')
    EMAIL_RE    = re.compile(r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')

    def __init__(self, master, app):
        super().__init__(master, fg_color=WHITE)
        self.app = app
        self.grid_columnconfigure((0,1), weight=1, uniform="half")
        self.grid_rowconfigure(0, weight=1)

        LeftImage(self, app.left_image_path).grid(row=0, column=0, sticky="nsew")
        right = ct.CTkFrame(self, fg_color=WHITE)
        right.grid(row=0, column=1, sticky="nsew", padx=60, pady=40)
        right.grid_columnconfigure(0, weight=1)

        ct.CTkLabel(right, text="Passwords Reset", font=F(32, "bold"),
                    text_color="black").grid(row=1, column=0, pady=(220,10))

        form = half_form(right, top_offset=0.38)
        ct.CTkLabel(form, text="Username", font=F(14), text_color="black", anchor="w").grid(row=0, column=0, sticky="w")
        self.username = entry_box(form, "Enter your username"); self.username.grid(row=1, column=0, pady=(0,8), sticky="ew")
        ct.CTkLabel(form, text="Email", font=F(14), text_color="black", anchor="w").grid(row=2, column=0, sticky="w")
        self.email = entry_box(form, "Enter your email"); self.email.grid(row=3, column=0, pady=(0,8), sticky="ew")

        primary_btn(form, "Continue", self.verify).grid(row=4, column=0, sticky="ew", pady=(10,8))

    def verify(self):
        u, e = self.username.get().strip(), self.email.get().strip()
        if not u or not e:
            messagebox.showwarning("Reset", "กรอกข้อมูลให้ครบ")
            return
        # ตรวจอังกฤษเท่านั้น 
            messagebox.showwarning("Reset", "Username ต้องเป็นภาษาอังกฤษ (≥6 ตัว, A–Z a–z 0–9 . _ - และเริ่มด้วยตัวอักษร)")
            return
        if not self.EMAIL_RE.match(e):
            messagebox.showwarning("Reset", "อีเมลไม่ถูกต้อง (ใช้ตัวอักษรภาษาอังกฤษเท่านั้น)")
            return

        if not self.app.db.match_user_email(u, e):
            messagebox.showerror("Reset", "Username/Email ไม่ตรงกัน")
            return
        self.app.reset_username = u
        self.app.show("ResetSet")



# ตั้งรหัสผ่านใหม่
class ResetSetPage(ct.CTkFrame):
    
    ASCII_RE = re.compile(r'^[\x20-\x7E]+$')

    def __init__(self, master, app):
        super().__init__(master, fg_color=WHITE)
        self.app = app
        self.grid_columnconfigure((0,1), weight=1, uniform="half")
        self.grid_rowconfigure(0, weight=1)

        LeftImage(self, app.left_image_path).grid(row=0, column=0, sticky="nsew")
        right = ct.CTkFrame(self, fg_color=WHITE)
        right.grid(row=0, column=1, sticky="nsew", padx=60, pady=40)
        right.grid_columnconfigure(0, weight=1)

        right.grid_rowconfigure(0, weight=0)  
        right.grid_rowconfigure(1, weight=1)   

        
        ct.CTkLabel(right, text="New Passwords", font=F(32, "bold"),
                    text_color="black")\
            .grid(row=0, column=0, pady=(220, 10))

        
        form = half_form(right, top_offset=0.38)



        # ช่องรหัสใหม่ 
        ct.CTkLabel(form, text="New Password", font=F(14), text_color="black", anchor="w")\
            .grid(row=0, column=0, sticky="w")

        pw_frame = ct.CTkFrame(form, fg_color=WHITE)
        pw_frame.grid(row=1, column=0, pady=(0,8), sticky="ew")
        pw_frame.grid_columnconfigure(0, weight=1)

        self.npw = entry_box(pw_frame, "New Password", show_char="•")
        self.npw.grid(row=0, column=0, sticky="ew")

        self.show_pw = tk.BooleanVar(value=False)
        ct.CTkButton(
            pw_frame, text="ㆅ", width=40, fg_color=GRAY_LIGHT, hover_color=GRAY_DARK,
            command=lambda: self.toggle_pw(self.npw, self.show_pw),
            text_color="black", font=F(14)
        ).grid(row=0, column=1, padx=(6,0))

        # ช่องยืนยันรหัสใหม่ 
        ct.CTkLabel(form, text="Confirm New Password", font=F(14), text_color="black", anchor="w")\
            .grid(row=2, column=0, sticky="w")

        cpw_frame = ct.CTkFrame(form, fg_color=WHITE)
        cpw_frame.grid(row=3, column=0, pady=(0,8), sticky="ew")
        cpw_frame.grid_columnconfigure(0, weight=1)

        self.cpw = entry_box(cpw_frame, "Confirm New Password", show_char="•")
        self.cpw.grid(row=0, column=0, sticky="ew")

        self.show_cpw = tk.BooleanVar(value=False)
        ct.CTkButton(
            cpw_frame, text="ㆅ", width=40, fg_color=GRAY_LIGHT, hover_color=GRAY_DARK,
            command=lambda: self.toggle_pw(self.cpw, self.show_cpw),
            text_color="black", font=F(14)
        ).grid(row=0, column=1, padx=(6,0))

        # ปุ่ม Submit ตั้งรหัส
        primary_btn(form, "Submit", self.set_pw).grid(row=4, column=0, sticky="ew", pady=(10,8))

    # ดูรหัสผ่าน
    def toggle_pw(self, entry, var):
        var.set(not var.get())
        entry.configure(show="" if var.get() else "•")

    def set_pw(self):
        u = self.app.reset_username
        if not u:
            messagebox.showwarning("Reset", "ทำขั้นตอนก่อนหน้าให้ครบก่อน")
            self.app.show("ResetRequest")
            return

        pw, cpw = self.npw.get(), self.cpw.get()

        # ===== บังคับภาษาอังกฤษเท่านั้น (ASCII พิมพ์ได้) =====
        if not self.ASCII_RE.match(pw) or not self.ASCII_RE.match(cpw):
            messagebox.showwarning(
                "Reset",
                "รหัสผ่านต้องใช้ภาษาอังกฤษ/ตัวเลข/สัญลักษณ์มาตรฐานเท่านั้น"
            )
            return

        
        if len(pw) < 8:
            messagebox.showwarning("Reset", "รหัสผ่านอย่างน้อย 8 ตัวอักษร")
            return
       
        if not re.search(r'[A-Z]', pw):
            messagebox.showwarning("Reset", "รหัสผ่านต้องมีตัวพิมพ์ใหญ่ อย่างน้อย 1 ตัว")
            return
        if not re.search(r'[0-9]', pw):
            messagebox.showwarning("Reset", "รหัสผ่านต้องมีตัวเลข อย่างน้อย 1 ตัว")
            return
     
        if pw != cpw:
            messagebox.showwarning("Reset", "รหัสผ่านไม่ตรงกัน")
            return

        ok, msg = self.app.db.set_new_password(u, pw)
        messagebox.showinfo("Reset", msg)
        if ok:
            self.app.show("SignIn")




# top bar user
class TopBar(ct.CTkFrame):
    def __init__(self, master, app, *args, **kwargs):
        super().__init__(master, fg_color=WHITE)
        self.app = app

        # layout: 0=logo, 1=spacer, 2=menu, 3=avatar
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=0)
        self.grid_columnconfigure(3, weight=0)

        # โลโก้ซ้าย
        left = ct.CTkFrame(self, fg_color=WHITE)
        left.grid(row=0, column=0, sticky="w", padx=36, pady=8)
        logo_box = image_widget(left, getattr(app, "logo_path", None), 100, 100, corner=12)
        logo_box.grid(row=0, column=0, sticky="w")

        # ปุ่มเมนูขวา
        btns = ct.CTkFrame(self, fg_color=WHITE)
        btns.grid(row=0, column=2, sticky="e", padx=(0, 12), pady=8)
        nav_btn(btns, "Home", lambda: self.app.show("Home")).grid(row=0, column=0, padx=10)
        nav_btn(btns, "Shopping Cart", lambda: self.app.show("Cart")).grid(row=0, column=1, padx=10)

        # โปรไฟล์
        self._avatar_size = 44
        self._avatar_btn = ct.CTkButton(
            self, text="", width=self._avatar_size, height=self._avatar_size,
            fg_color="transparent", hover=False,
            image=self.app.get_current_avatar_ctkimage(self._avatar_size),
            command=lambda: self.app.show("UserProfile")
        )
        self._avatar_btn.grid(row=0, column=3, padx=(0, 24), pady=8, sticky="e")

    def refresh_avatar(self):
        self._avatar_btn.configure(image=self.app.get_current_avatar_ctkimage(self._avatar_size))








#้home 
class HomePage(ct.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color=WHITE)
        self.app = app
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        TopBar(self, app).grid(row=0, column=0, sticky="ew")

        self.body = ct.CTkScrollableFrame(self, fg_color=WHITE)
        self.body.grid(row=1, column=0, sticky="nsew", padx=30, pady=20)
        self.body.grid_columnconfigure(0, weight=1)
        hide_scrollbar(self.body)

        self.render_products()

    # แสดงรายการสินค้า
    def render_products(self):
        # ล้างของเก่า
        for w in self.body.winfo_children():
            w.destroy()

        # ดึงสินค้าจากฐานข้อมูล
        products = self.app.db.list_products()

        #โชว์เฉพาะสินค้าที่มีสต๊อก
        available = []
        for rec in products:
            if len(rec) == 4:
                pid, name, price, stock = rec
                img_path = None
            else:
                pid, name, price, stock, img_path = rec

            if stock and int(stock) > 0:
                available.append((pid, name, price, stock, img_path))

        # ไม่มีสินค้าในสต๊อก
        if not available:
            ct.CTkLabel(self.body, text="สินค้าที่พร้อมจำหน่ายหมดชั่วคราว",
                        text_color="black", font=F(18)).pack(pady=30)
            ct.CTkLabel(self.body, text="ทั้งหมด 0 รายการ",
                        text_color="#7b7b7b", font=F(14)).pack(pady=(8,0))
            return

        # วางกริดการ์ดสินค้า
        grid = ct.CTkFrame(self.body, fg_color=WHITE)
        grid.pack(fill="x", expand=True)

        # ปรับระยะขอบซ้ายขวาตามขนาดหน้าต่าง
        grid.pack_configure(
            padx=(int(self.winfo_width()*0.05) if self.winfo_width() else 120,
                int(self.winfo_width()*0.05) if self.winfo_width() else 120)
        )
        
        COLS, IMG_W, IMG_H = 4, 260, 260
        for i in range(COLS):
            grid.grid_columnconfigure(i, weight=1, uniform="cardcol")

        # วางการ์ดเฉพาะสินค้าที่เหลือขาย
        for idx, (pid, name, price, stock, img_path) in enumerate(available):
            r, c = divmod(idx, COLS)
            card = ct.CTkFrame(grid, fg_color=WHITE, border_width=1,
                            border_color="#e8e8e8", corner_radius=16)
            card.grid(row=r, column=c, sticky="nsew", padx=10, pady=10)
            card.grid_columnconfigure(0, weight=1)

            img_box = image_widget(card, img_path, IMG_W, IMG_H, corner=16)
            img_box.grid(row=0, column=0, pady=(12,8), sticky="n")

            meta = ct.CTkFrame(card, fg_color=WHITE)
            meta.grid(row=1, column=0, sticky="ew", padx=12)
            meta.grid_columnconfigure(0, weight=1)
            meta.grid_columnconfigure(1, weight=0)

            #ชื่อสินค้า 
            ct.CTkLabel(
                meta,
                text=str(name),
                text_color="black",
                font=F(14, "bold"),
                justify="left",     
                wraplength=180      
            ).grid(row=0, column=0, sticky="w")

            ct.CTkLabel(meta, text=f"จำนวน {int(stock):,} ชิ้น", text_color="#666666", font=F(12))\
                .grid(row=0, column=1, sticky="e", padx=(10,0))
            ct.CTkLabel(meta, text=f"{int(price):,} บาท", text_color="#333333", font=F(14))\
                .grid(row=1, column=0, sticky="w", pady=(2,0))

            # แถวปรับจำนวน
            qty_row = ct.CTkFrame(card, fg_color=WHITE)
            qty_row.grid(row=2, column=0, sticky="ew", padx=12, pady=(6,12))
            qty_var   = tk.IntVar(value=1)
            max_stock = int(stock)

            # ปรับจำนวนสินค้า
            def change(delta, var=qty_var, mx=max_stock):
                new = var.get() + delta
                if new < 1: new = 1
                if new > mx:
                    new = mx
                    messagebox.showinfo("จำนวนเกิน", f"มีสินค้า {mx:,} ชิ้น")
                var.set(new)

            # ปุ่ม + - และช่องแสดงจำนวน
            ct.CTkButton(qty_row, text="-", width=34, fg_color=GRAY_LIGHT, hover_color=GRAY_DARK,
                        text_color="black", command=lambda v=qty_var, m=max_stock: change(-1, v, m),
                        font=F(14)).pack(side="left", padx=(0,4))
            ct.CTkEntry(qty_row, width=56, justify="center", textvariable=qty_var,
                        fg_color=GRAY_LIGHT, border_color="#e0e0e0", font=F(14)).pack(side="left")
            ct.CTkButton(qty_row, text="+", width=34, fg_color=GRAY_LIGHT, hover_color=GRAY_DARK,
                        text_color="black", command=lambda v=qty_var, m=max_stock: change(+1, v, m),
                        font=F(14)).pack(side="left", padx=(4,0))

            # เพิ่มสินค้าลงตะกร้า
            def add_to_cart(pid=pid, name=name, mx=max_stock, var=qty_var):
                want = int(var.get())
                in_cart = int(self.app.cart.get(pid, 0))
                can_add = mx - in_cart
                if can_add <= 0:
                    messagebox.showwarning("ตะกร้า", "สินค้าในตะกร้ามีจำนวนครบแล้ว")
                    return
                if want > can_add:
                    want = can_add
                    messagebox.showinfo("จำนวนถูกปรับ", f"เพิ่มได้สูงสุดอีก {can_add:,} ชิ้น")
                self.app.cart[pid] = in_cart + want
                messagebox.showinfo("Cart", f"เพิ่ม {name} x{want} ลงตะกร้าแล้ว")
                var.set(1)

            # #ปุ่มเพิ่มลงตะกร้า
            primary_btn(card, "เพิ่มลงตะกร้า", add_to_cart)\
                .grid(row=3, column=0, sticky="ew", padx=12, pady=(0,12))

        # แสดงจำนวนเฉพาะที่พร้อมขาย
        ct.CTkLabel(self.body, text=f"ทั้งหมด {len(available)} รายการ",
                    text_color="#7b7b7b", font=F(14)).pack(pady=(8,0))
        
        # หลังจาก page.tkraise() และ page.refresh() (ถ้ามี)
        try:
            for p in self.pages.values():
                for ch in p.winfo_children():
                    if isinstance(ch, TopBar):
                        ch.refresh_avatar()
        except Exception:
            pass
        
    # เพิ่มใน class HomePage
    def refresh(self):
        # รีเฟรชรายการสินค้าบนหน้า Home
        self.render_products()





#ตระกร้าสินค้า shopping cart
class CartPage(ct.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color=WHITE)
        self.app = app

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        TopBar(self, app).grid(row=0, column=0, sticky="ew")

        title = ct.CTkLabel(self, text="Shopping Cart",
                            font=F(36, "bold"),
                            text_color="black")
        title.grid(row=1, column=0, sticky="w", padx=50, pady=(10,0))

        self.content = ct.CTkFrame(self, fg_color=WHITE)
        self.content.grid(row=2, column=0, sticky="nsew", padx=40, pady=10)
        self.content.grid_rowconfigure(0, weight=1)
        self.content.grid_columnconfigure(0, weight=1) 
        self.content.grid_columnconfigure(1, weight=5)  
        self.content.grid_columnconfigure(2, weight=3)

        self.spacer = ct.CTkFrame(self.content, fg_color=WHITE, width=1, height=1)
        self.spacer.grid(row=0, column=0, sticky="ns")

        self.list_frame = ct.CTkScrollableFrame(self.content, fg_color=WHITE)
        self.list_frame.grid(row=0, column=1, sticky="nsew", padx=(0,20))
        hide_scrollbar(self.list_frame)

        self.summary = ct.CTkFrame(self.content, fg_color=WHITE,
                                   border_width=1, border_color="#dddddd",
                                   corner_radius=16)
        self.summary.grid(row=0, column=2, sticky="n", ipadx=10, ipady=10)

        self.bind("<Configure>", lambda e: self._resize_spacer())
        self._resize_spacer()

        self.refresh()

    # ลบสินค้าออกจากตระกร้า
    def _resize_spacer(self):
        try:
            self.update_idletasks()
            w = max(0, self.content.winfo_width())
            target = max(120, int(w * 0.15))
            self.content.grid_columnconfigure(0, minsize=target)
        except Exception:
            pass

    # ลบสินค้าออกจากตระกร้า
    def refresh(self):
        target = getattr(self.list_frame, "_scrollable_frame", self.list_frame)
        for w in target.winfo_children():
            w.destroy()
        for w in self.summary.winfo_children():
            w.destroy()

        total = 0
        rowi = 0
        for pid, qty in self.app.cart.items():
            rec = self.app.db.get_product(pid)
            if not rec:
                continue
            _id, name, price, stock, image_path = rec

            item_total = int(price) * int(qty)
            total += item_total

            # สร้างการ์ดแต่ละสินค้า
            card = ct.CTkFrame(self.list_frame, fg_color=WHITE, border_width=1, border_color="#dddddd", corner_radius=16)
            card.grid(row=rowi, column=0, sticky="ew", pady=10, padx=8)
            card.grid_columnconfigure(1, weight=1)

            img = image_widget(card, image_path, 160, 160, corner=16)
            img.grid(row=0, column=0, padx=16, pady=16)

            # ชื่อสินค้า
            name_lbl = ct.CTkLabel(
                card,
                text=name,
                font=F(18, "bold"),
                text_color="black",
                justify="left",
                wraplength=280 
            )
            name_lbl.grid(row=0, column=1, sticky="w", pady=(8, 4))

            right_col = ct.CTkFrame(card, fg_color=WHITE)
            right_col.grid(row=0, column=2, padx=12)

            # ปุ่มลบสินค้า
            ct.CTkButton(right_col, text="🗑", width=36, fg_color=GRAY_LIGHT, hover_color=GRAY_DARK, text_color="black",
                        command=lambda pid=pid: self.remove_item(pid), font=F(16)).grid(row=0, column=0, pady=(12, 0))

            # กล่องจำนวนสินค้า
            qty_box = ct.CTkFrame(card, fg_color=WHITE)
            qty_box.grid(row=1, column=1, sticky="w", pady=(0, 12))
            ct.CTkButton(qty_box, text="-", width=36, fg_color=GRAY_LIGHT, hover_color=GRAY_DARK, text_color="black",
                        command=lambda pid=pid: self.change_qty(pid, -1), font=F(16)).grid(row=0, column=0, padx=4)
            ct.CTkLabel(qty_box, text=str(qty), text_color="black", font=F(14)).grid(row=0, column=1)
            ct.CTkButton(qty_box, text="+", width=36, fg_color=GRAY_LIGHT, hover_color=GRAY_DARK, text_color="black",
                        command=lambda pid=pid: self.change_qty(pid, +1), font=F(16)).grid(row=0, column=2, padx=4)

            # แสดงราคารวมต่อชิ้น
            ct.CTkLabel(card, text=f"ราคา {item_total:,} บาท", text_color="black", font=F(14))\
                .grid(row=1, column=2, sticky="e", padx=16, pady=(0, 12))

            rowi += 1

        # สรุปรายการสินค้า
        ct.CTkLabel(self.summary, text="Order Summary", font=F(22, "bold"), text_color="black")\
            .grid(row=0, column=0, sticky="w", padx=18, pady=(12, 6))
        sep = ct.CTkFrame(self.summary, height=1, fg_color="#dddddd")
        sep.grid(row=1, column=0, sticky="ew", padx=12)

        # ข้อมูลสรุป
        info = ct.CTkFrame(self.summary, fg_color=WHITE)
        info.grid(row=2, column=0, sticky="ew", padx=18, pady=10)
        ct.CTkLabel(info, text="Items", text_color="#7b7b7b", font=F(14)).grid(row=0, column=0, sticky="w")
        ct.CTkLabel(info, text=f"{sum(self.app.cart.values())} ชิ้น", text_color="black", font=F(14))\
            .grid(row=0, column=1, sticky="e", padx=(80, 0))
        ct.CTkLabel(info, text="Sub Total", text_color="#7b7b7b", font=F(14)).grid(row=1, column=0, sticky="w")
        ct.CTkLabel(info, text=f"{total:,} บาท", text_color="black", font=F(14))\
            .grid(row=1, column=1, sticky="e", padx=(80, 0))

        #เส้นคั่น
        sep2 = ct.CTkFrame(self.summary, height=1, fg_color="#dddddd")
        sep2.grid(row=3, column=0, sticky="ew", padx=12, pady=(6, 6))
        
        total_row = ct.CTkFrame(self.summary, fg_color=WHITE)
        total_row.grid(row=4, column=0, sticky="ew", padx=18, pady=(0, 12))
        ct.CTkLabel(total_row, text="Total", font=F(18, "bold"), text_color="#6f6f6f").grid(row=0, column=0, sticky="w")
        ct.CTkLabel(total_row, text=f"{total:,} บาท", font=F(18, "bold"), text_color="black")\
            .grid(row=0, column=1, sticky="e", padx=(80, 0))
        
        # ปุ่มไปหน้า Checkout
        primary_btn(self.summary, "Checkout", lambda: self.app.goto_checkout())\
            .grid(row=5, column=0, padx=18, pady=(6, 18), sticky="ew")

    # ลบสินค้าออกจากตระกร้า
    def remove_item(self, pid):
        if pid in self.app.cart: del self.app.cart[pid]
        self.refresh()
        

    # ปรับจำนวนสินค้าในตะกร้า
    def change_qty(self, pid, delta):
        if pid not in self.app.cart: return
        rec = self.app.db.get_product(pid)
        if not rec: return
        _id, name, price, stock, *_ = rec
        stock = int(stock) if stock is not None else 999999
        newq = self.app.cart[pid] + delta
        if newq < 1: newq = 1
        if newq > stock:
            newq = stock
            messagebox.showinfo("จำนวนสินค้าเกิน", f"{name} มีจำนวน {stock:,} ชิ้น")
        self.app.cart[pid] = newq
        self.refresh()
        
    
        try:
            for p in self.pages.values():
                for ch in p.winfo_children():
                    if isinstance(ch, TopBar):
                        ch.refresh_avatar()
        except Exception:
            pass
        
     




# สร้างรูปโปรไฟล์วงกลม CTkImage
def make_ctk_circle_image(path: str | None, size=56):
    try:
        if path and os.path.exists(path):
            im = Image.open(path).convert("RGBA")
        else:
            im = Image.new("RGBA", (size, size), (230,230,230,255))
        im = ImageOps.fit(im, (size, size), Image.LANCZOS)
        mask = Image.new("L", (size, size), 0)
        ImageDraw.Draw(mask).ellipse((0, 0, size-1, size-1), fill=255)
        im.putalpha(mask)
        return CTkImage(light_image=im, size=(size, size))
    except Exception:
        ph = Image.new("RGBA", (size, size), (230,230,230,255))
        return CTkImage(light_image=ph, size=(size, size))


# เปิดไฟล์
def open_file_auto(path: str):
    try:
        # Windows
        if os.name == "nt":
            os.startfile(path)
            return
        # macOS / Linux
        
        cmd = ["open", path] if sys.platform == "darwin" else ["xdg-open", path]
        subprocess.Popen(cmd)
    except Exception:
        # fallback เปิดผ่านเบราว์เซอร์ (Edge/Chrome มักเปิด PDF ได้)
        try:
            
            webbrowser.open_new("file:///" + path.replace("\\", "/"))
        except Exception:
            pass


# โปรไฟล์ผู้ใช้
class ProfilePage(ct.CTkFrame):

    def __init__(self, master, app):
        super().__init__(master, fg_color=WHITE)
        self.app = app
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        TopBar(self, app).grid(row=0, column=0, sticky="ew")

        body = ct.CTkFrame(self, fg_color=WHITE)
        body.grid(row=2, column=0, sticky="n", padx=60, pady=(10,30))

        card = ct.CTkFrame(body, fg_color=WHITE, corner_radius=24,
                           border_width=2, border_color="#e5e5e5")
        card.grid(row=0, column=0, padx=10, pady=10, sticky="n")

        # สร้างรูปโปรไฟล์วงกลมเป็น
        self._av_imgtk = make_ctk_circle_image(
            getattr(self.app, "app_image_path", None),  
            size=140
        )

      
        av_lbl = ct.CTkLabel(card, image=self._av_imgtk, text="", fg_color=WHITE)
  
        av_lbl.grid(row=0, column=0, pady=(0,10))


        self.name_lbl  = ct.CTkLabel(card, text="ชื่อผู้ใช้งาน", font=F(34, "bold"), text_color="black")
        self.email_key = ct.CTkLabel(card, text="Email :", font=F(16), text_color="black")
        self.email_val = ct.CTkLabel(card, text="—", font=F(16), text_color="black")

        self.name_lbl.grid(row=1, column=0, columnspan=2, pady=(6,10))
        self.email_key.grid(row=2, column=0, sticky="e", padx=(40,6))
        self.email_val.grid(row=2, column=1, sticky="w", padx=(6,40))

        # ปุ่ม
        ct.CTkButton(card, text="แก้ไขข้อมูล", fg_color=GRAY_LIGHT, hover_color=GRAY_DARK,
                     text_color="black", command=lambda: self.app.show("ProfileEdit"), font=F(14))\
            .grid(row=3, column=0, columnspan=2, pady=(14,10))
        primary_btn(card, "Log out", self.app.logout).grid(row=4, column=0, columnspan=2, pady=(6,12))
        primary_btn(body, "Order History", lambda: self.app.show("OrderHistory")).grid(row=1, column=0, pady=(18,0))


        self._avatar_label = av_lbl

    def refresh(self):
        u = self.app.current_user
        if not u:
            self.app.show("SignIn"); return
        row = self.app.db.get_user(u)
        if row:
            uname, email, pimg = row
            self.name_lbl.configure(text=uname)
            self.email_val.configure(text=email or "—")
            imgtk = circle_avatar_image(pimg, 160)
            self._av_imgtk = imgtk
            self._avatar_label.configure(image=imgtk)




# ประวัติคำสั่งซื้อ
class OrderHistoryPage(ct.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color=WHITE)
        self.app = app
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        TopBar(self, app).grid(row=0, column=0, sticky="ew")

        # Back
        ct.CTkButton(self, text="Back", width=100, height=36,
                     fg_color=BLUE_LIGHT, hover_color=BLUE_DARK, text_color="black",
                     corner_radius=18, command=lambda: self.app.show("Profile"), font=F(16))\
            .grid(row=1, column=0, sticky="w", padx=50, pady=(6,0))

        ct.CTkLabel(self, text="Order History", font=F(36, "bold"), text_color="black")\
            .grid(row=2, column=0, pady=(6, 6))

        self.body = ct.CTkScrollableFrame(self, fg_color=WHITE)
        self.body.grid(row=3, column=0, sticky="nsew", padx=40, pady=(4,16))
        hide_scrollbar(self.body)

    def refresh(self):
    
        for w in self.body.winfo_children(): w.destroy()

        u = self.app.current_user
        if not u:
            ct.CTkLabel(self.body, text="กรุณาเข้าสู่ระบบ", font=F(18), text_color="black").pack(pady=20)
            return

        orders = self.app.db.list_orders_by_user(u)
        if not orders:
            ct.CTkLabel(self.body, text="ยังไม่มีประวัติคำสั่งซื้อ", font=F(18), text_color="black").pack(pady=20)
            return

        for (order_id, cname, phone, addr, total, created_at, pay_img) in orders:
            card = ct.CTkFrame(self.body, fg_color=WHITE, corner_radius=20,
                               border_width=1, border_color="#dedede")
            card.pack(fill="x", padx=10, pady=12)

            inner = ct.CTkFrame(card, fg_color=WHITE); inner.pack(fill="x", padx=22, pady=16)

    
            hdr = ct.CTkFrame(inner, fg_color=GRAY_LIGHT, corner_radius=16); hdr.pack(anchor="w", pady=(0,10))
            ct.CTkLabel(hdr, text=f"ORDER ID:  {order_id}", font=F(24, "bold"), text_color="black")\
                .pack(padx=14, pady=6)

            # ข้อมูลผู้สั่งซื้อ
            info = ct.CTkFrame(inner, fg_color=WHITE); info.pack(anchor="w", pady=(2,8))
            for r, (k, v) in enumerate([
                ("ชื่อ :", cname), ("เบอร์โทร :", phone), ("ที่อยู่ :", addr)
            ]):
                ct.CTkLabel(info, text=k, font=F(15), text_color="black").grid(row=r, column=0, sticky="w", padx=(4,8), pady=2)
                ct.CTkLabel(info, text=v, font=F(15), text_color="black").grid(row=r, column=1, sticky="w", pady=2)

            # หัวตาราง
            ct.CTkLabel(inner, text="คำสั่งซื้อ", font=F(20,"bold"), text_color="black").pack(anchor="w", pady=(6,6))
            table = ct.CTkFrame(inner, fg_color=WHITE); table.pack(fill="x")
            table.grid_columnconfigure(0, weight=4); table.grid_columnconfigure(1, weight=1); table.grid_columnconfigure(2, weight=1)

            ct.CTkLabel(table, text="ชื่อสินค้า", font=F(16,"bold"), text_color="black").grid(row=0, column=0, sticky="w")
            ct.CTkLabel(table, text="จำนวนที่สั่ง", font=F(16,"bold"), text_color="black").grid(row=0, column=1, sticky="e")
            ct.CTkLabel(table, text="ราคา", font=F(16,"bold"), text_color="black").grid(row=0, column=2, sticky="e")
            ct.CTkFrame(table, height=1, fg_color="#e5e5e5").grid(row=1, column=0, columnspan=3, sticky="ew", pady=(7,7))

            r = 2
            for pname, qty, price_each, sub_total in self.app.db.get_order_items(order_id):
                ct.CTkLabel(table, text=pname, font=F(15), text_color="black").grid(row=r, column=0, sticky="w", pady=2)
                ct.CTkLabel(table, text=str(qty), font=F(15), text_color="black").grid(row=r, column=1, sticky="e", pady=2)
                ct.CTkLabel(table, text=f"{sub_total:,} บาท", font=F(15), text_color="black").grid(row=r, column=2, sticky="e", pady=2)
                r += 1

            ct.CTkFrame(table, height=1, fg_color="#e5e5e5").grid(row=r, column=0, columnspan=3, sticky="ew", pady=(8,8))
            r += 1
            ct.CTkLabel(table, text="ราคารวมทั้งหมด", font=F(18,"bold"), text_color="black").grid(row=r, column=1, sticky="e")
            ct.CTkLabel(table, text=f"{int(total):,} บาท", font=F(18,"bold"), text_color="black").grid(row=r, column=2, sticky="e")

            # ปุ่ม Open Receipt
            ct.CTkButton(inner, text="Open Receipt", width=150,
                         fg_color=BLUE_LIGHT, hover_color=BLUE_DARK, text_color="black", font=F(16),
                         command=lambda oid=order_id: self._open_receipt(oid)).pack(pady=(12,0), anchor="center")

    def _open_receipt(self, order_id):
        # เปิดไฟล์ใบเสร็จ PDF
        base = os.path.dirname(DB_PATH)
        pdf_path = os.path.join(base, "receipts", f"{order_id}.pdf")
        if os.path.exists(pdf_path):
            open_file_auto(pdf_path)
        else:
            messagebox.showwarning("Receipt", "ยังไม่พบไฟล์ใบเสร็จของออเดอร์นี้")
            
    
        try:
            for p in self.pages.values():
                for ch in p.winfo_children():
                    if isinstance(ch, TopBar):
                        ch.refresh_avatar()
        except Exception:
            pass



# หน้า Checkout
class CheckoutPage(ct.CTkFrame):
    GO_HOME_DELAY_MS = 1000
    def __init__(self, master, app):
        super().__init__(master, fg_color=WHITE)
        self.app = app

        self.grid_columnconfigure(0, weight=1)
        TopBar(self, app).grid(row=0, column=0, sticky="ew")

        self.body = ct.CTkScrollableFrame(self, fg_color=WHITE)
        self.body.grid(row=1, column=0, sticky="nsew", padx=30, pady=10)
        self.grid_rowconfigure(1, weight=1)

        self.summary_frame = None
        self.total_var = tk.StringVar(value="0 บาท")
        self.upload_box = None
        self.upload_path = None
        self.user_preview_label = None

        self.name_entry = None
        self.phone_entry = None
        self.addr_entry = None

        self._build_static()
        hide_scrollbar(self.body)

    
    def _resolve_home_key(self):
        try:
            if "Home" in self.app.pages:
                return "Home"
            for k in self.app.pages.keys():
                if k.lower().startswith("home"):
                    return k
        except Exception:
            pass
        return "Home"

    def _force_go_home(self):

        key = self._resolve_home_key()
        def _do():
            try:
                self.app.show(key)
                page = self.app.pages.get(key)
                if hasattr(page, "refresh"):
                    page.refresh()
                if hasattr(self.app, "refresh_all_topbars"):
                    self.app.refresh_all_topbars()
            except Exception:
                pass

        self.after_idle(_do)
        self.after(60, _do)

    def _scroll_top(self):

        try:
            canvas = getattr(self.body, "_parent_canvas", None) or getattr(self.body, "_canvas", None)
            if canvas:
                canvas.yview_moveto(0)
        except Exception:
            pass

    # ล้างฟอร์ม
    def reset_form(self):

        try:
            for ent in (self.name_entry, self.phone_entry, self.addr_entry):
                ent.delete(0, "end")
        except Exception:
            pass
        self.upload_path = None
        try:
            self.user_preview_label.configure(image=None, text="(ยังไม่เลือกรูป)")
            self.user_preview_label.image = None
        except Exception:
            pass

    
    def _build_static(self):
        ct.CTkLabel(self.body, text="Checkout", text_color="black",
                    font=F(45, "bold")).pack(anchor="w", pady=(8,0))

        self.summary_frame = ct.CTkFrame(
            self.body, fg_color=WHITE, border_width=1,
            border_color="#e8e8e8", corner_radius=12
        )
        self.summary_frame.pack(fill="x", expand=True, padx=0, pady=(10,20))

        up_wrap = ct.CTkFrame(self.body, fg_color=WHITE)
        up_wrap.pack(fill="x", pady=(0,20))
        ct.CTkLabel(up_wrap, text="อัปโหลดหลักฐานการชำระเงิน",
                    text_color="black", font=F(36, "bold")).pack(anchor="w", pady=(0,8))

        row = ct.CTkFrame(up_wrap, fg_color=WHITE)
        row.pack(fill="x")

        self.upload_box = ct.CTkFrame(row, fg_color=WHITE, corner_radius=12, width=300, height=300)
        self.upload_box.grid(row=0, column=0, sticky="w", padx=(0,20), pady=(4,12))
        self.upload_box.grid_propagate(False)

        right = ct.CTkFrame(row, fg_color=WHITE)
        right.grid(row=0, column=1, sticky="w")

        self.upload_btn = ct.CTkButton(
            right, text="อัปโหลดภาพ",
            fg_color=GRAY_LIGHT, hover_color=GRAY_DARK, text_color="black",
            command=self._pick_image, font=F(14)
        )
        self.upload_btn.grid(row=0, column=0, sticky="w", pady=(4,10))

        preview = ct.CTkFrame(right, fg_color=WHITE, width=160, height=160,
                              border_color="#e5e5e5", border_width=1, corner_radius=12)
        preview.grid(row=1, column=0, sticky="w")
        preview.grid_propagate(False)
        self.user_preview_label = tk.Label(preview, bg=WHITE, bd=0, highlightthickness=0, text="ไม่มีรูปภาพ")
        self.user_preview_label.place(relx=0.5, rely=0.5, anchor="center")

        # Shipping Address
        ship = ct.CTkFrame(self.body, fg_color=WHITE)
        ship.pack(fill="x", pady=(10,30))
        ct.CTkLabel(ship, text="Shipping Address",
                    text_color="black", font=F(35, "bold")
                    ).pack(anchor="w", pady=(0,10))

        form = ct.CTkFrame(ship, fg_color=WHITE); form.pack(anchor="w")

        ct.CTkLabel(form, text="ชื่อ - สกุล *", text_color="black",font=F(16))\
            .grid(row=0, column=0, sticky="w", pady=(0,6))
        self.name_entry = entry_box(form, "กรอกชื่อ-สกุล")
        self.name_entry.configure(width=360)
        self.name_entry.grid(row=1, column=0, sticky="w", pady=(0, 10))

        ct.CTkLabel(form, text="หมายเลขโทรศัพท์ *", text_color="black",font=F(16)).grid(row=2, column=0, sticky="w")
        vcmd = (self.register(self._validate_phone), "%P")
        self.phone_entry = entry_box(form, "0xx-xxx-xxxx")
        self.phone_entry.configure(width=360, validate="key", validatecommand=vcmd)
        self.phone_entry.grid(row=3, column=0, sticky="w", pady=(0, 10))

        ct.CTkLabel(form, text="ที่อยู่ *", text_color="black",font=F(16)).grid(row=4, column=0, sticky="w")
        self.addr_entry = entry_box(form, "บ้านเลขที่ / ถนน / ตำบล / อำเภอ / จังหวัด / รหัสไปรษณีย์")
        self.addr_entry.configure(width=600)
        self.addr_entry.grid(row=5, column=0, sticky="w")

        primary_btn(self.body, "บันทึก", self._save_checkout)\
            .pack(anchor="center", pady=(16, 30))

    # เลือกภาพหลักฐานการชำระเงิน
    def refresh(self):

        self.reset_form()
        self.populate()
        self.after_idle(self._scroll_top)

    # บันทึกคำสั่งซื้อ
    def populate(self):
        self._load_system_image()
        for w in self.summary_frame.winfo_children():
            w.destroy()

        head = ct.CTkFrame(self.summary_frame, fg_color=WHITE)
        head.pack(fill="x", padx=18, pady=(14,6))
        ct.CTkLabel(head, text="รายการคำสั่งซื้อ:", font=F(25, "bold"), text_color="black").pack(anchor="w")

        table = ct.CTkFrame(self.summary_frame, fg_color=WHITE)
        table.pack(fill="x", padx=18, pady=(0,12))
        table.grid_columnconfigure(0, weight=3)
        table.grid_columnconfigure(1, weight=1)
        table.grid_columnconfigure(2, weight=1)
        table.grid_columnconfigure(3, weight=1)

        hdr_font = F(16, "bold")
        ct.CTkLabel(table, text="ชื่อสินค้า", text_color="#444", font=hdr_font).grid(row=0, column=0, sticky="w", padx=(6,6))
        ct.CTkLabel(table, text="จำนวน",   text_color="#444", font=hdr_font).grid(row=0, column=1, sticky="e", padx=(6,6))
        ct.CTkLabel(table, text="ราคา",    text_color="#444", font=hdr_font).grid(row=0, column=2, sticky="e", padx=(6,6))
        ct.CTkLabel(table, text="รวม",     text_color="#444", font=hdr_font).grid(row=0, column=3, sticky="e", padx=(6,6))

        ct.CTkFrame(table, height=1, fg_color="#e5e5e5").grid(row=1, column=0, columnspan=4, sticky="ew", pady=(6,8))

        total, r = 0, 2
        for pid, qty in self.app.cart.items():
            rec = self.app.db.get_product(pid)
            if not rec:
                continue
            if len(rec) == 4:
                _id, name, price, _stock = rec
            else:
                _id, name, price, _stock, _img = rec
            sub = int(price) * int(qty); total += sub
            ct.CTkLabel(table, text=name, text_color="black",font=F(16)).grid(row=r, column=0, sticky="w", padx=(6,6))
            ct.CTkLabel(table, text=str(qty), text_color="black",font=F(16)).grid(row=r, column=1, sticky="e", padx=(6,6))
            ct.CTkLabel(table, text=f"{int(price):,} บาท", text_color="black",font=F(16)).grid(row=r, column=2, sticky="e", padx=(6,6))
            ct.CTkLabel(table, text=f"{sub:,} บาท",       text_color="black",font=F(16)).grid(row=r, column=3, sticky="e", padx=(6,6))
            r += 1

        ct.CTkFrame(table, height=1, fg_color="#e5e5e5").grid(row=r, column=0, columnspan=4, sticky="ew", pady=(8,6))
        r += 1
        ct.CTkLabel(table, text="รวมทั้งหมด", font=F(20, "bold"), text_color="black").grid(row=r, column=2, sticky="e", padx=(6,6))
        ct.CTkLabel(table, text=f"{total:,} บาท", font=F(20, "bold"), text_color="black").grid(row=r, column=3, sticky="e", padx=(6,6))
        self.total_var.set(f"{total:,} บาท")

        self.after_idle(self._scroll_top)

    # โหลดรูปภาพหลักฐานการชำระเงินจากระบบ 
    def _load_system_image(self):
        for w in self.upload_box.winfo_children():
            w.destroy()
        app_img_path = getattr(self.app, "app_image_path", None)
        CANVAS = 700
        if app_img_path and os.path.exists(app_img_path):
            try:
                img = Image.open(app_img_path)
                img.thumbnail((400, 400), Image.LANCZOS)
                canvas = Image.new("RGB", (CANVAS, CANVAS), "white")
                ox = (CANVAS - img.width) // 2
                oy = (CANVAS - img.height) // 2
                canvas.paste(img, (ox, oy))
                tkimg = ImageTk.PhotoImage(canvas)
                lbl = tk.Label(self.upload_box, image=tkimg, border=0, bg=WHITE)
                lbl.image = tkimg
                lbl.place(relx=0.5, rely=0.5, anchor="center")
            except Exception:
                pass

    def _validate_phone(self, new_text: str) -> bool:
        if new_text == "":
            return True
        return new_text.isdigit() and len(new_text) <= 10

    def _pick_image(self):
        path = filedialog.askopenfilename(
            title="เลือกไฟล์รูปภาพ",
            filetypes=[("Image files","*.png;*.jpg;*.jpeg;*.webp;*.bmp")]
        )
        if not path:
            return
        self.upload_path = path
        try:
            img = Image.open(path)
            if img.mode not in ("RGB", "RGBA"):
                img = img.convert("RGBA")
            img.thumbnail((150, 150), Image.LANCZOS)
            tkimg = ImageTk.PhotoImage(img)
            self.user_preview_label.configure(image=tkimg, text="")
            self.user_preview_label.image = tkimg
            self.upload_btn.configure(fg_color=GRAY_LIGHT, hover_color=GRAY_DARK, text_color="black")
        except Exception as e:
            messagebox.showerror("Upload", f"ไม่สามารถเปิดไฟล์ภาพได้\n{e}")

    def _save_checkout(self):

        # ตรวจสอบข้อมูล 
        name  = self.name_entry.get().strip()
        phone = self.phone_entry.get().strip()
        addr  = self.addr_entry.get().strip()
        if not name or not phone or not addr:
            messagebox.showwarning("Checkout", "กรอกข้อมูลที่อยู่ให้ครบ")
            return
        if not self.app.cart:
            messagebox.showwarning("Checkout", "ตะกร้าว่างเปล่า")
            return

        # บันทึกออเดอร์ 
        cart_items = list(self.app.cart.items())
        order_id, total = self.app.db.create_order(
            self.app.current_user or "guest", name, phone, addr, cart_items
        )

        # เซฟหลักฐานโอน
        pdf_path = None
        if self.upload_path:
            try:
                pay_dir = os.path.join(os.path.dirname(DB_PATH), "payments")
                os.makedirs(pay_dir, exist_ok=True)
                ext = os.path.splitext(self.upload_path)[1].lower() or ".png"
                save_path = os.path.join(pay_dir, f"{order_id}{ext}")

                img = Image.open(self.upload_path)
                if img.mode not in ("RGB", "RGBA"):
                    img = img.convert("RGB")
                img.save(save_path)

                self.app.db.c.execute("UPDATE orders SET payment_image=? WHERE order_id=?", (save_path, order_id))
                self.app.db.conn.commit()
            except Exception as e:
                print("save payment image error:", e)

        # สร้าง PDF
        try:
            pdf_path = make_receipt_pdf(self.app, order_id)
        except Exception as e:
            print("make_receipt_pdf error:", e)
            pdf_path = None

        # เตรียมข้อความแจ้ง 
        if pdf_path:
            msg = (
                f"บันทึกออเดอร์สำเร็จ\n"
                f"ORDER ID: {order_id}\n"
                f"ยอดรวม    {total:,} บาท\n\n"
                f"ใบเสร็จถูกสร้างที่:\n{pdf_path}"
            )
        else:
            msg = (
                f"บันทึกออเดอร์สำเร็จ\n"
                f"ORDER ID: {order_id}\n"
                f"ยอดรวม    {total:,} บาท\n\n"
                f"(หมายเหตุ: สร้างใบเสร็จ PDF ไม่สำเร็จ)"
            )

       
        messagebox.showinfo("Checkout", msg)

        try:
            if pdf_path and os.path.exists(pdf_path):

                self.after(10, lambda: open_file_auto(pdf_path))
            else:
                pass
            
        except Exception as e:
            print("open_file_auto error:", e)
        try:
            self.app.cart.clear()
            for ent in (self.name_entry, self.phone_entry, self.addr_entry):
                ent.delete(0, "end")
            self.upload_path = None
            self.user_preview_label.configure(image=None, text="(ยังไม่เลือกรูป)")
            self.user_preview_label.image = None
        except Exception:
            pass


        def _go_home():
            try:
                self.app.show("Home")
                home = self.app.pages.get("Home")
                if hasattr(home, "refresh"):
                    home.refresh()
                if hasattr(self.app, "refresh_all_topbars"):
                    self.app.refresh_all_topbars()
            except Exception:
                pass
        self.after(1000, _go_home)










#top bar admin
class AdminTopBar(ct.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color=WHITE)
        self.app = app
        self.grid_columnconfigure(0, weight=1)

        left = ct.CTkFrame(self, fg_color=WHITE)
        left.grid(row=0, column=0, sticky="w", padx=36, pady=8)
        logo_box = image_widget(left, getattr(app, "logo_path", None), 100, 100, corner=12)
        logo_box.grid(row=0, column=0, sticky="w")
        ct.CTkLabel(left, text="ADMIN", text_color="black", font=F(28, "bold"))\
            .grid(row=0, column=1, padx=(16, 0), sticky="w")

        btns = ct.CTkFrame(self, fg_color=WHITE)
        btns.grid(row=0, column=1, sticky="e", padx=36)

        nav_btn(btns, "Product",   lambda: app.show("AdminDashboard")).grid(row=0, column=0, padx=10)
        nav_btn(btns, "Add",       lambda: app.show("AdminAdd")).grid(row=0, column=1, padx=10)
        nav_btn(btns, "Remove",    lambda: app.show("AdminRemove")).grid(row=0, column=2, padx=10)
        nav_btn(btns, "Stock",     lambda: app.show("AdminStock")).grid(row=0, column=3, padx=10)
        nav_btn(btns, "Order",     lambda: app.show("AdminOrders")).grid(row=0, column=4, padx=10)
        nav_btn(btns, "Dashboard", lambda: app.show("AdminSummary")).grid(row=0, column=5, padx=10)
        nav_btn(btns, "Log out",   lambda: app.logout(), primary=True).grid(row=0, column=6, padx=10)





# หน้าแดชบอร์ดสำหรับแอดมิน (แสดงรายการสินค้า)
class AdminDashboardPage(ct.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color=WHITE)
        self.app = app
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        AdminTopBar(self, app).grid(row=0, column=0, sticky="ew")

        self.body = ct.CTkScrollableFrame(self, fg_color=WHITE)
        self.body.grid(row=2, column=0, sticky="nsew", padx=30, pady=10)
        self.body.grid_columnconfigure(0, weight=1)
        hide_scrollbar(self.body)

        # 
        self.grid = None

        self.render()

    def _clear_body(self):
        for w in self.body.winfo_children():
            try:
                w.destroy()
            except Exception:
                pass
        self.grid = None

    def render(self):
        
        self._clear_body()

        # โหลดสินค้า
        products = self.app.db.list_products() or []

        # ถ้าไม่มีสินค้า แสดงข้อความแล้วจบ
        if not products:
            ct.CTkLabel(
                self.body, text="ยังไม่มีสินค้าในฐานข้อมูล",
                text_color="black", font=F(18)
            ).pack(pady=30)
            return

        # กรอบตารางหลัก
        self.grid = ct.CTkFrame(self.body, fg_color=WHITE)
        self.grid.pack(fill="x", expand=True)

        # ปรับระยะขอบ
        sw = max(1, self.winfo_screenwidth())
        gutter = int(sw * 0.10)
        self.grid.pack_configure(padx=(gutter, gutter))

        # ตั้งคอลัมน์
        COLS = 4
        IMG_W, IMG_H = 260, 260
        CARD_W = IMG_W + 40
        CARD_H = IMG_H + 120

        for i in range(COLS):
            self.grid.grid_columnconfigure(i, weight=1, uniform="acol")

        # วาดการ์ดสินค้า
        for idx, rec in enumerate(products):
         
            if len(rec) == 4:
                pid, name, price, stock = rec
                img_path = None
            else:
                pid, name, price, stock, img_path = rec

            r, c = divmod(idx, COLS)

            card = ct.CTkFrame(
                self.grid,
                fg_color=WHITE,
                border_width=1,
                border_color="#e8e8e8",
                corner_radius=18,
                width=CARD_W,
                height=CARD_H
            )
            card.grid(row=r, column=c, sticky="nsew", padx=12, pady=20)
            card.grid_propagate(False)
            card.grid_columnconfigure(0, weight=1)

            img_box = image_widget(card, img_path, IMG_W, IMG_H, corner=16)
            img_box.grid(row=0, column=0, padx=12, pady=(12, 8), sticky="n")

            meta = ct.CTkFrame(card, fg_color=WHITE)
            meta.grid(row=1, column=0, sticky="ew", padx=12)
            meta.grid_columnconfigure(0, weight=1)
            meta.grid_columnconfigure(1, weight=0)

            ct.CTkLabel(
                meta, text=name, text_color="black",
                font=F(14, "bold"), justify="left", wraplength=180
            ).grid(row=0, column=0, sticky="w")

            ct.CTkLabel(
                meta, text=f"สต๊อก {int(stock):,} ชิ้น",
                text_color="#666", font=F(12)
            ).grid(row=0, column=1, sticky="e")

            ct.CTkLabel(
                meta, text=f"{int(price):,} บาท",
                text_color="#333", font=F(14)
            ).grid(row=1, column=0, sticky="w", pady=(2, 0))

 
    def refresh(self):
        self.render()


    def on_db_changed(self):
        self.render()

    



# add เพิ่มสินค้าใหม่
class AdminAddPage(ct.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color=WHITE)
        self.app = app
        self.image_src = None  # path รูปภาพที่ผู้ใช้เลือก

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        AdminTopBar(self, app).grid(row=0, column=0, sticky="ew")

        form = ct.CTkFrame(self, fg_color=WHITE)
        form.grid(row=2, column=0, sticky="n", pady=(10, 0))
        form.grid_columnconfigure(0, weight=1)

        ct.CTkLabel(form, text="ชื่อสินค้า", text_color="black", font=F(14)).grid(row=0, column=0, sticky="w")
        self.name_e = entry_box(form, "เช่น สินค้ารุ่นพิเศษ"); self.name_e.configure(width=520)
        self.name_e.grid(row=1, column=0, sticky="w", pady=(0, 10))

        ct.CTkLabel(form, text="จำนวน", text_color="black", font=F(14)).grid(row=2, column=0, sticky="w")
        vnum = (self.register(lambda s: s.isdigit() or s == ""), "%P")
        self.stock_e = entry_box(form, "ตัวเลขเท่านั้น"); self.stock_e.configure(width=520, validate="key", validatecommand=vnum)
        self.stock_e.grid(row=3, column=0, sticky="w", pady=(0, 10))

        ct.CTkLabel(form, text="ราคา", text_color="black", font=F(14)).grid(row=4, column=0, sticky="w")
        self.price_e = entry_box(form, "ตัวเลขเท่านั้น"); self.price_e.configure(width=520, validate="key", validatecommand=vnum)
        self.price_e.grid(row=5, column=0, sticky="w", pady=(0, 16))

        preview_wrap = ct.CTkFrame(form, fg_color=WHITE)
        preview_wrap.grid(row=6, column=0, sticky="n", pady=(2, 8))
        preview_wrap.grid_columnconfigure(0, weight=1)

        self.preview_box = ct.CTkFrame(preview_wrap, fg_color="#eeeeee",
                                       width=260, height=260, corner_radius=12)
        self.preview_box.grid(row=0, column=0, pady=(0, 10))
        self.preview_box.grid_propagate(False)
        tk.Label(self.preview_box, text="ไม่มีรูป", bg="#eeeeee")\
          .place(relx=0.5, rely=0.5, anchor="center")

        ct.CTkButton(preview_wrap, text="อัปโหลดรูปภาพ",
                     fg_color=GRAY_LIGHT, hover_color=GRAY_LIGHT, text_color="black",
                     command=self.pick_image, font=F(14))\
          .grid(row=1, column=0, pady=(0, 8))

        # #ปุ่มบันทึกสินค้า
        primary_btn(form, "บันทึก", self.save_item)\
            .grid(row=7, column=0, pady=(10, 24))

    #อัปโหลดรูปสินค้า
    def pick_image(self):
        p = filedialog.askopenfilename(
            title="เลือกรูปสินค้า",
            filetypes=[("รูปภาพ", "*.png;*.jpg;*.jpeg;*.webp;*.bmp")]
        )
        if not p:
            return
        self.image_src = p
        for w in self.preview_box.winfo_children(): w.destroy()
        try:
            img = Image.open(p)
            img.thumbnail((240, 240), Image.LANCZOS)
            imgtk = ImageTk.PhotoImage(img)
            lbl = tk.Label(self.preview_box, image=imgtk, bg="#eeeeee")
            lbl.image = imgtk
            lbl.place(relx=0.5, rely=0.5, anchor="center")
        except Exception as e:
            messagebox.showerror("อัปโหลดรูป", f"ไม่สามารถเปิดรูปได้\n{e}")

    # #รีเซ็ตหน้า
    def reset_form(self):
        try:
            self.name_e.delete(0, tk.END)
            self.stock_e.delete(0, tk.END)
            self.price_e.delete(0, tk.END)
        except Exception:
            pass

        self.image_src = None
        for w in self.preview_box.winfo_children():
            w.destroy()
        tk.Label(self.preview_box, text="ไม่มีรูป", bg="#eeeeee")\
          .place(relx=0.5, rely=0.5, anchor="center")

    # บันทึกสินค้าใหม่
    def save_item(self):
        name = self.name_e.get().strip()
        stock = self.stock_e.get().strip()
        price = self.price_e.get().strip()

        if not (name and stock.isdigit() and price.isdigit()):
            messagebox.showwarning("Add", "กรอกชื่อ/จำนวน/ราคา ให้ครบและถูกต้อง")
            return
        
        # บันทึกรูปภาพสินค้า
        img_path = None
        if self.image_src:
            try:
                folder = os.path.join(os.path.dirname(DB_PATH), "product_images")
                os.makedirs(folder, exist_ok=True)
                ext = os.path.splitext(self.image_src)[1].lower() or ".png"
                safe_name = re.sub(r'[\\/:*?"<>|]+', "_", name)
                img_path = os.path.join(folder, f"{safe_name}{ext}")
                Image.open(self.image_src).save(img_path)
            except Exception:
                img_path = None
                


        self.app.db.add_product(name, int(price), int(stock), img_path)
        messagebox.showinfo("Add", "บันทึกสินค้าเรียบร้อย")

        try:
            if "Products" in self.app.pages and hasattr(self.app.pages["Products"], "refresh"):
                self.app.pages["Products"].refresh()
        except Exception:
            pass
        try:
            if "Home" in self.app.pages and hasattr(self.app.pages["Home"], "refresh"):
                self.app.pages["Home"].refresh()
        except Exception:
            pass

        # รีเซ็ตฟอร์ม
        self.reset_form()

        # กลับหน้าแดชบอร์ด
        self.app.show("AdminDashboard")

          
        


#remove ลบหรือแก้ไขสินค้า
class AdminRemovePage(ct.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color=WHITE)
        self.app = app

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        AdminTopBar(self, app).grid(row=0, column=0, sticky="ew")

        title = ct.CTkLabel(self, text="เพิ่ม ลด จำนวนสินค้า",
                            font=F(28, "bold"),
                            text_color="black")
        title.grid(row=1, column=0, sticky="w", padx=50, pady=(10, 10))

        table_frame = ct.CTkFrame(self, fg_color=WHITE)
        table_frame.grid(row=2, column=0, sticky="nsew", padx=100, pady=(0, 20))
        table_frame.grid_columnconfigure(0, weight=1)
        table_frame.grid_rowconfigure(0, weight=1)

        style = ttk.Style()
        style.configure("Custom.Treeview", font=(APP_FONT_FAMILY, 14), rowheight=34)
        style.configure("Custom.Treeview.Heading", font=(APP_FONT_FAMILY, 16, "bold"))

        self.tree = ttk.Treeview(table_frame, columns=("id", "name", "stock", "price"),
                                 show="headings", style="Custom.Treeview", height=12)
        self.tree.heading("id", text="ID")
        self.tree.heading("name", text="ชื่อสินค้า")
        self.tree.heading("stock", text="จำนวนสินค้า")
        self.tree.heading("price", text="ราคา")

        self.tree.column("id", width=60, anchor="center")
        self.tree.column("name", width=220, anchor="w")
        self.tree.column("stock", width=180, anchor="e")   
        self.tree.column("price", width=160, anchor="e")

        self.tree.grid(row=0, column=0, sticky="nsew")

        self.refresh_table()
        
       
        try:
            if "Home" in self.app.pages:
                self.app.pages["Home"].render_products()        
        except Exception:
            pass

        

        btn_frame = ct.CTkFrame(self, fg_color=WHITE)
        btn_frame.grid(row=3, column=0, pady=(0, 40))

        primary_btn(btn_frame, "เพิ่มจำนวน", self.increase_stock).pack(pady=8)
        primary_btn(btn_frame, "ลดจำนวน", self.decrease_stock).pack(pady=8)
        primary_btn(btn_frame, "แก้ไขราคา", self.edit_price).pack(pady=8)
        primary_btn(btn_frame, "ลบสินค้า", self.remove_item).pack(pady=8)

    
    def _fmt_num(self, n):
        try:
            return f"{int(n):,}"
        except:
            try:
                return f"{float(str(n).replace(',', '')):,.2f}"
            except:
                return str(n)

    def _parse_int(self, s):

        return int(str(s).replace(",", "").strip())

    def refresh_table(self):
        # ลบของเก่า
        for i in self.tree.get_children():
            self.tree.delete(i)
        # เติมใหม่พร้อมใส่ comma ทุกตัวเลข
        for row in self.app.db.list_products():
            if len(row) == 4:
                pid, name, price, stock = row
            else:
                pid, name, price, stock, _ = row

            pid_disp   = self._fmt_num(pid)
            stock_disp = self._fmt_num(stock)
            price_disp = self._fmt_num(price)

            self.tree.insert("", "end", values=(pid_disp, name, stock_disp, price_disp))

    def refresh(self):
        self.refresh_table()


    def increase_stock(self):
        self._change_stock(delta=1)

    def decrease_stock(self):
        self._change_stock(delta=-1)

    # แก้ไขราคาสินค้า
    def edit_price(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("แก้ไขราคา", "กรุณาเลือกสินค้าที่ต้องการแก้ราคา")
            return
        item = self.tree.item(sel[0])
        pid_disp, name, stock_disp, price_disp = item["values"]

        pid   = self._parse_int(pid_disp)
        price = self._parse_int(price_disp)

        new_price = simpledialog.askinteger(
            "แก้ไขราคา",
            f"ราคาปัจจุบัน {self._fmt_num(price)} บาท\nกรอกราคาที่ต้องการใหม่:"
        )
        if new_price is not None:
            self.app.db.c.execute("UPDATE products SET price=? WHERE id=?", (int(new_price), pid))
            self.app.db.conn.commit()
            messagebox.showinfo("สำเร็จ", f"อัปเดตราคาของ {name} เป็น {self._fmt_num(new_price)} บาทแล้ว")
            self.refresh_table()

    # ลบสินค้า
    def remove_item(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("ลบสินค้า", "กรุณาเลือกสินค้าที่ต้องการลบ")
            return
        item = self.tree.item(sel[0])
        pid_disp, name, *_ = item["values"]
        pid = self._parse_int(pid_disp)

        if not messagebox.askyesno("ยืนยันการลบ", f"ต้องการลบ {name} ใช่หรือไม่?"):
            return
        
        try:
            self.app.db.delete_product(pid)  
        except Exception as e:
            messagebox.showerror("ลบสินค้า", f"ลบไม่สำเร็จ: {e}")
            return

        # รีเฟรชตารางหน้านี้
        self.refresh_table()

        # รีเฟรชหน้าอื่นที่แสดงสินค้า/สรุปยอดให้เห็นผลทันที
        try:
            if "Home" in self.app.pages and hasattr(self.app.pages["Home"], "render_products"):
                self.app.pages["Home"].render_products()
        except Exception:
            pass
        try:
            if "AdminDashboard" in self.app.pages and hasattr(self.app.pages["AdminDashboard"], "refresh"):
                self.app.pages["AdminDashboard"].refresh()
        except Exception:
            pass

        messagebox.showinfo("ลบสำเร็จ", f"ลบ {name} แล้ว")


    # เปลี่ยนแปลงสต๊อกสินค้า
    def _change_stock(self, delta):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("ปรับจำนวน", "กรุณาเลือกสินค้า")
            return
        item = self.tree.item(sel[0])
        pid_disp, name, stock_disp, price_disp = item["values"]

        pid   = self._parse_int(pid_disp)
        stock = self._parse_int(stock_disp)

        new_stock = max(0, stock + delta)
        self.app.db.c.execute("UPDATE products SET stock=? WHERE id=?", (new_stock, pid))
        self.app.db.conn.commit()


        messagebox.showinfo("สำเร็จ", f"จำนวนของ {name} เป็น {self._fmt_num(new_stock)} ชิ้นแล้ว")
        self.refresh_table()
        
        # รีเฟรช Products/Home เพื่อสะท้อนสต๊อกใหม่
        try:
            if "Products" in self.app.pages and hasattr     (self.app.pages["Products"], "refresh"):
                self.app.pages["Products"].refresh()
        except Exception:
            pass
        try:
            if "Home" in self.app.pages and hasattr(self.       app.pages["Home"], "refresh"):
                self.app.pages["Home"].refresh()
        except Exception:
            pass



# หน้าสต๊อกสินค้า 
class AdminStockPage(ct.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color=WHITE)
        self.app = app

        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Top Bar
        AdminTopBar(self, app).grid(row=0, column=0, sticky="ew")

        # Title
        ct.CTkLabel(
            self, text="Stock",
            font=F(42, "bold"), text_color="black"
        ).grid(row=1, column=0, sticky="w", padx=40, pady=(10, 10))

        # Scrollable Body
        self.body = ct.CTkScrollableFrame(self, fg_color=WHITE)
        self.body.grid(row=2, column=0, sticky="nsew", padx=40, pady=(0, 20))
        hide_scrollbar(self.body)

        self.refresh()


    def refresh(self):

    
        for w in self.body.winfo_children():
            w.destroy()


        wrapper = ct.CTkFrame(self.body, fg_color=WHITE)
        wrapper.pack(pady=10)
        wrapper.grid_columnconfigure((0,1,2), weight=1)

 
        header = ct.CTkFrame(wrapper, fg_color="#e6e6e6", corner_radius=12)
        header.grid(row=0, column=0, columnspan=3, sticky="ew", pady=(0, 5))
        header.grid_columnconfigure((0,1,2), weight=1)

        widths = [450, 180, 180]
        headers = ["ชื่อสินค้า", "จำนวนสินค้า", "ราคา"]

        for i, (text, w) in enumerate(zip(headers, widths)):

            anchor_pos = "w"
            sticky_pos = "w"

            if i == 2:        # คอลัมน์ราคา
                anchor_pos = "e"
                sticky_pos = "e"

            ct.CTkLabel(
                header, text=text, width=w,
                anchor=anchor_pos, font=F(20, "bold"),
                text_color="black"
            ).grid(row=0, column=i, padx=10, pady=14, sticky=sticky_pos)


      
        products = self.app.db.list_products_full()  

        r = 1
        for pid, name, price, stock, img_path in products:

            row = ct.CTkFrame(wrapper, fg_color=WHITE)
            row.grid(row=r, column=0, columnspan=3, sticky="ew", pady=4)
            row.grid_columnconfigure((0,1,2), weight=1)

            # ชื่อสินค้า
            ct.CTkLabel(
                row, text=name, width=widths[0],
                anchor="w", font=F(18)
            ).grid(row=0, column=0, padx=10, pady=6, sticky="w")

            # จำนวนสต๊อก
            ct.CTkLabel(
                row, text=str(stock), width=widths[1],
                anchor="center", font=F(18)
            ).grid(row=0, column=1, padx=10)

            # ราคา
            ct.CTkLabel(
                row, text=f"{price:,} บาท", width=widths[2],
                anchor="e", font=F(18)
            ).grid(row=0, column=2, padx=10, sticky="e")

            r += 1





#orders
class AdminOrdersPage(ct.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color=WHITE)
        self.app = app

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        AdminTopBar(self, app).grid(row=0, column=0, sticky="ew")

        # แถวปุ่มย่อย 
        sub = ct.CTkFrame(self, fg_color=WHITE)
        sub.grid(row=1, column=0, sticky="w", padx=50, pady=(6, 0))
        # ปุ่ม All Order 
        ct.CTkButton(sub, text="All  Order", font=F(16), width=110, height=36,
                     fg_color=BLUE_LIGHT, hover_color=BLUE_DARK, text_color="black",
                     corner_radius=18, command=lambda: self.app.show("AdminAllOrders")
                     ).pack(side="left", padx=(0,12))
        # ปุ่ม Order 
        ct.CTkButton(sub, text="Order", font=F(16), width=90, height=36,
                     fg_color=BLUE_DARK, hover_color=BLUE_DARK, text_color="white",
                     corner_radius=18, command=lambda: self.app.show("AdminOrders")
                     ).pack(side="left")

        title = ct.CTkLabel(self, text="Orders", font=F(36, "bold"), text_color="black")
        title.grid(row=2, column=0, sticky="w", padx=50, pady=(10, 0))

        self.body = ct.CTkScrollableFrame(self, fg_color=WHITE)
        self.body.grid(row=3, column=0, sticky="nsew", padx=40, pady=10)
        hide_scrollbar(self.body)

 
    def _format_created_at(self, value):
        try:
            if value is None:
                return "-"
            s = str(value).strip()
            if s.isdigit():
                dt = datetime.fromtimestamp(int(s))
                return dt.strftime("%d/%m/%Y")

            try:
                f = float(s)
                if abs(f) > 1000000000:
                    dt = datetime.fromtimestamp(f)
                    return dt.strftime("%d/%m/%Y")

            except:
                pass
            s2 = s.replace("T", " ")
            try:
                dt = datetime.fromisoformat(s2)
            except:
                try:
                    dt = datetime.strptime(s2, "%Y-%m-%d")
                except:
                    return s
            return dt.strftime("%d/%m/%Y")

        except:
            return str(value) if value is not None else "-"

    # รีเฟรชหน้า
    def refresh(self):
        for w in self.body.winfo_children():
            w.destroy()

        orders = self.app.db.list_orders()
        if not orders:
            ct.CTkLabel(self.body, text="ยังไม่มีคำสั่งซื้อเข้ามา", text_color="black", font=F(18)).pack(pady=30)
            return

        # แสดงคำสั่งซื้อ
        for order in orders:
            if len(order) >= 7:
                order_id, cname, phone, addr, total, created_at, pay_img = order
            else:
                order_id, cname, phone, addr, total, created_at = order
                pay_img = None

            card = ct.CTkFrame(self.body, fg_color=WHITE, corner_radius=18,
                               border_width=1, border_color="#dedede")
            card.pack(fill="x", padx=10, pady=14)

            inner = ct.CTkFrame(card, fg_color=WHITE)
            inner.pack(fill="both", padx=22, pady=20)

            # พรีวิวหลักฐาน 
            proof = ct.CTkFrame(inner, fg_color=WHITE)
            proof.place(relx=0.93, rely=0.05, anchor="ne")
            ct.CTkLabel(proof, text="หลักฐานการชำระเงิน",
                        font=F(20, "bold"), text_color="black").pack(anchor="e", pady=(0, 6))
            PROOF_W, PROOF_H = 150, 150
            proof_box = ct.CTkFrame(
                proof, fg_color=WHITE, border_width=1, border_color="#e5e5e5",
                corner_radius=12, width=PROOF_W, height=PROOF_H
            )
            proof_box.pack()
            proof_box.grid_propagate(False)
            try:
                if pay_img and os.path.exists(pay_img):
                    img = Image.open(pay_img)
                    img_ratio = img.width / img.height
                    box_ratio = PROOF_W / PROOF_H
                    if img_ratio >= box_ratio:
                        new_w = PROOF_W - 2
                        new_h = int(new_w / img_ratio)
                    else:
                        new_h = PROOF_H - 2
                        new_w = int(new_h * img_ratio)
                    img = img.resize((new_w, new_h), Image.LANCZOS)
                    canvas = Image.new("RGB", (PROOF_W, PROOF_H), "white")
                    ox = (PROOF_W - new_w) // 2
                    oy = (PROOF_H - new_h) // 2
                    canvas.paste(img, (ox, oy))
                    tkimg = ImageTk.PhotoImage(canvas)
                    lbl = tk.Label(proof_box, image=tkimg, bg=WHITE, border=0)
                    lbl.image = tkimg
                    lbl.place(relx=0.5, rely=0.5, anchor="center")
                else:
                    tk.Label(proof_box, text="ไม่มีรูป", bg=WHITE).place(relx=0.5, rely=0.5, anchor="center")
            except Exception:
                tk.Label(proof_box, text="ไม่มีรูป", bg=WHITE).place(relx=0.5, rely=0.5, anchor="center")

            
            hdr = ct.CTkFrame(inner, fg_color=GRAY_LIGHT, corner_radius=20)
            hdr.pack(anchor="w", pady=(0, 12))
            order_datetime_text = self._format_created_at(created_at)
            ct.CTkLabel(
                hdr,
                text=f"ORDER ID:  {order_id}   ·   วันที่สั่งซื้อ: {order_datetime_text}",
                font=F(28, "bold"),
                text_color="black"
            ).pack(padx=16, pady=10)

            # ข้อมูลลูกค้า
            info = ct.CTkFrame(inner, fg_color=WHITE)
            info.pack(anchor="w", pady=(7, 9))
            ct.CTkLabel(info, text=f"ชื่อ :  {cname}",    font=F(15), text_color="black").grid(row=0, column=0, sticky="w", pady=(0,4))
            ct.CTkLabel(info, text=f"เบอร์โทร :  {phone}", font=F(15), text_color="black").grid(row=1, column=0, sticky="w", pady=(0,4))
            ct.CTkLabel(info, text=f"ที่อยู่ :  {addr}",   font=F(15), text_color="black").grid(row=2, column=0, sticky="w")

            # รายการสินค้า
            ct.CTkLabel(inner, text="คำสั่งซื้อ", font=F(22, "bold"), text_color="black").pack(anchor="w", pady=(8, 7))
            table = ct.CTkFrame(inner, fg_color=WHITE)
            table.pack(fill="x")
            table.grid_columnconfigure(0, weight=4)
            table.grid_columnconfigure(1, weight=1)
            table.grid_columnconfigure(2, weight=1)

            hdrf = F(16, "bold")
            ct.CTkLabel(table, text="ชื่อสินค้า",   font=hdrf, text_color="black").grid(row=0, column=0, sticky="w")
            ct.CTkLabel(table, text="จำนวนที่สั่ง", font=hdrf, text_color="black").grid(row=0, column=1, sticky="e")
            ct.CTkLabel(table, text="ราคา",       font=hdrf, text_color="black").grid(row=0, column=2, sticky="e")

            ct.CTkFrame(table, height=1, fg_color="#e5e5e5").grid(row=1, column=0, columnspan=3, sticky="ew", pady=(7,9))

            r = 2
            for pname, qty, price_each, sub_total in self.app.db.get_order_items(order_id):
                ct.CTkLabel(table, text=pname, font=F(16), text_color="black").grid(row=r, column=0, sticky="w", pady=3)
                ct.CTkLabel(table, text=str(qty), font=F(16), text_color="black").grid(row=r, column=1, sticky="e", pady=3)
                ct.CTkLabel(table, text=f"{sub_total:,} บาท", font=F(16), text_color="black").grid(row=r, column=2, sticky="e", pady=3)
                r += 1

            ct.CTkFrame(table, height=1, fg_color="#e5e5e5").grid(row=r, column=0, columnspan=3, sticky="ew", pady=(9,9))
            r += 1
            ct.CTkLabel(table, text="ราคารวมทั้งหมด", font=F(19, "bold"), text_color="black").grid(row=r, column=1, sticky="e")
            ct.CTkLabel(table, text=f"{int(total):,} บาท", font=F(19, "bold"), text_color="black").grid(row=r, column=2, sticky="e")

            # ปุ่ม mark as done
            ct.CTkButton(inner, text="Mark as Done", width=160,corner_radius=18,
                         fg_color=BLUE_LIGHT, hover_color=BLUE_DARK, text_color="black",
                         font=F(18), command=lambda oid=order_id, c=card: self._done(oid, c)).pack(pady=(17, 7))


    def _done(self, oid, card_widget):
        if messagebox.askyesno("ยืนยัน", f"ปิดงานออเดอร์ {oid} ?"):
            # อัปเดตสถานะแทนการลบ
            self.app.db.mark_order_done(oid, 1)
            # เอาการ์ดออกเฉพาะจากหน้ารายการงานค้าง
            try:
                card_widget.destroy()
            except Exception:
                pass







class AdminAllOrdersPage(ct.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color=WHITE)
        self.app = app

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        AdminTopBar(self, app).grid(row=0, column=0, sticky="ew")

        # ปุ่มย่อย
        sub = ct.CTkFrame(self, fg_color=WHITE)
        sub.grid(row=1, column=0, sticky="w", padx=50, pady=(6, 0))
        ct.CTkButton(sub, text="All  Order", font=F(16), width=110, height=36,
                     fg_color=BLUE_DARK, hover_color=BLUE_DARK, text_color="white",
                     corner_radius=18, command=lambda: self.app.show("AdminAllOrders")
                     ).pack(side="left", padx=(0,12))
        ct.CTkButton(sub, text="Order", font=F(16), width=90, height=36,
                     fg_color=BLUE_LIGHT, hover_color=BLUE_DARK, text_color="black",
                     corner_radius=18, command=lambda: self.app.show("AdminOrders")
                     ).pack(side="left")

        title = ct.CTkLabel(self, text="All Orders (History)", font=F(36, "bold"), text_color="black")
        title.grid(row=2, column=0, sticky="w", padx=50, pady=(10, 0))

        self.body = ct.CTkScrollableFrame(self, fg_color=WHITE)
        self.body.grid(row=3, column=0, sticky="nsew", padx=40, pady=10)
        hide_scrollbar(self.body)

    def _format_created_at(self, value):
  
        try:
            if value is None:
                return "-"
            s = str(value).strip()
 
            if s.isdigit():
                dt = datetime.fromtimestamp(int(s))
                return dt.strftime("%d/%m/%Y")


            try:
                f = float(s)
                if abs(f) > 1000000000:  # น่าจะเป็น timestamp วินาที
                    dt = datetime.fromtimestamp(f)
                    return dt.strftime("%d/%m/%Y")

            except:
                pass
        
            s2 = s.replace("T", " ")
            try:
                dt = datetime.fromisoformat(s2)
            except:
                try:
                    dt = datetime.strptime(s2, "%Y-%m-%d ")
                except:
                    return s  
            return dt.strftime("%d/%m/%Y ")
        except:
            return str(value) if value is not None else "-"

    def refresh(self):
        for w in self.body.winfo_children():
            w.destroy()

        orders = self.app.db.list_orders()
        if not orders:
            ct.CTkLabel(self.body, text="ยังไม่มีคำสั่งซื้อเข้ามา", text_color="black", font=F(18)).pack(pady=30)
            return

        # แสดงคำสั่งซื้อ
        for order in orders:
            if len(order) >= 7:
                order_id, cname, phone, addr, total, created_at, pay_img = order
            else:
                order_id, cname, phone, addr, total, created_at = order
                pay_img = None

            card = ct.CTkFrame(self.body, fg_color=WHITE, corner_radius=18,
                               border_width=1, border_color="#dedede")
            card.pack(fill="x", padx=10, pady=14)

            inner = ct.CTkFrame(card, fg_color=WHITE)
            inner.pack(fill="both", padx=22, pady=20)

            # พรีวิวหลักฐาน 
            proof = ct.CTkFrame(inner, fg_color=WHITE)
            proof.place(relx=0.93, rely=0.05, anchor="ne")
            ct.CTkLabel(proof, text="หลักฐานการชำระเงิน",
                        font=F(20, "bold"), text_color="black").pack(anchor="e", pady=(0, 6))
            PROOF_W, PROOF_H = 150, 150
            proof_box = ct.CTkFrame(
                proof, fg_color=WHITE, border_width=1, border_color="#e5e5e5",
                corner_radius=12, width=PROOF_W, height=PROOF_H
            )
            proof_box.pack()
            proof_box.grid_propagate(False)
            try:
                if pay_img and os.path.exists(pay_img):
                    img = Image.open(pay_img)
                    img_ratio = img.width / img.height
                    box_ratio = PROOF_W / PROOF_H
                    if img_ratio >= box_ratio:
                        new_w = PROOF_W - 2
                        new_h = int(new_w / img_ratio)
                    else:
                        new_h = PROOF_H - 2
                        new_w = int(new_h * img_ratio)
                    img = img.resize((new_w, new_h), Image.LANCZOS)
                    canvas = Image.new("RGB", (PROOF_W, PROOF_H), "white")
                    ox = (PROOF_W - new_w) // 2
                    oy = (PROOF_H - new_h) // 2
                    canvas.paste(img, (ox, oy))
                    tkimg = ImageTk.PhotoImage(canvas)
                    lbl = tk.Label(proof_box, image=tkimg, bg=WHITE, border=0)
                    lbl.image = tkimg
                    lbl.place(relx=0.5, rely=0.5, anchor="center")
                else:
                    tk.Label(proof_box, text="ไม่มีรูป", bg=WHITE).place(relx=0.5, rely=0.5, anchor="center")
            except Exception:
                tk.Label(proof_box, text="ไม่มีรูป", bg=WHITE).place(relx=0.5, rely=0.5, anchor="center")

    
            order_datetime_text = self._format_created_at(created_at)
            hdr = ct.CTkFrame(inner, fg_color=GRAY_LIGHT, corner_radius=20)
            hdr.pack(anchor="w", pady=(0, 12))
            ct.CTkLabel(
                hdr,
                text=f"ORDER ID:  {order_id}   ·   วันที่สั่งซื้อ: {order_datetime_text}",
                font=F(28, "bold"),
                text_color="black"
            ).pack(padx=16, pady=10)

            # ข้อมูลลูกค้า
            info = ct.CTkFrame(inner, fg_color=WHITE)
            info.pack(anchor="w", pady=(7, 9))
            ct.CTkLabel(info, text=f"ชื่อ :  {cname}",    font=F(15), text_color="black").grid(row=0, column=0, sticky="w", pady=(0,4))
            ct.CTkLabel(info, text=f"เบอร์โทร :  {phone}", font=F(15), text_color="black").grid(row=1, column=0, sticky="w", pady=(0,4))
            ct.CTkLabel(info, text=f"ที่อยู่ :  {addr}",   font=F(15), text_color="black").grid(row=2, column=0, sticky="w")

            # รายการสินค้า
            ct.CTkLabel(inner, text="คำสั่งซื้อ", font=F(22, "bold"), text_color="black").pack(anchor="w", pady=(8, 7))
            table = ct.CTkFrame(inner, fg_color=WHITE)
            table.pack(fill="x")
            table.grid_columnconfigure(0, weight=4)
            table.grid_columnconfigure(1, weight=1)
            table.grid_columnconfigure(2, weight=1)

            hdrf = F(16, "bold")
            ct.CTkLabel(table, text="ชื่อสินค้า",   font=hdrf, text_color="black").grid(row=0, column=0, sticky="w")
            ct.CTkLabel(table, text="จำนวนที่สั่ง", font=hdrf, text_color="black").grid(row=0, column=1, sticky="e")
            ct.CTkLabel(table, text="ราคา",       font=hdrf, text_color="black").grid(row=0, column=2, sticky="e")

            ct.CTkFrame(table, height=1, fg_color="#e5e5e5").grid(row=1, column=0, columnspan=3, sticky="ew", pady=(7,9))

            r = 2
            for pname, qty, price_each, sub_total in self.app.db.get_order_items(order_id):
                ct.CTkLabel(table, text=pname, font=F(16), text_color="black").grid(row=r, column=0, sticky="w", pady=3)
                ct.CTkLabel(table, text=str(qty), font=F(16), text_color="black").grid(row=r, column=1, sticky="e", pady=3)
                ct.CTkLabel(table, text=f"{sub_total:,} บาท", font=F(16), text_color="black").grid(row=r, column=2, sticky="e", pady=3)
                r += 1

            ct.CTkFrame(table, height=1, fg_color="#e5e5e5").grid(row=r, column=0, columnspan=3, sticky="ew", pady=(9,9))
            r += 1
            ct.CTkLabel(table, text="ราคารวมทั้งหมด", font=F(19, "bold"), text_color="black").grid(row=r, column=1, sticky="e")
            ct.CTkLabel(table, text=f"{int(total):,} บาท", font=F(19, "bold"), text_color="black").grid(row=r, column=2, sticky="e")


# หน้าสรุปยอดขายรายวัน รายเดือน และรวมทั้งหมด
class AdminSummaryPage(ct.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color=WHITE)
        self.app = app

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        
        AdminTopBar(self, app).grid(row=0, column=0, sticky="ew")

        self.scroll = ct.CTkScrollableFrame(
            self, fg_color=WHITE, corner_radius=0
        )
        self.scroll.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)
        self.scroll.grid_columnconfigure(0, weight=1)


        hide_scrollbar(self.scroll)

  
        ct.CTkLabel(
            self.scroll,
            text="Dashboard",
            font=F(48, "bold"),
            text_color="black"
        ).grid(row=0, column=0, sticky="w", padx=50, pady=(10, 20))

 
        self.body = ct.CTkFrame(self.scroll, fg_color=WHITE)
        self.body.grid(row=1, column=0, sticky="nsew", padx=40, pady=20)
        self.body.grid_columnconfigure((0, 1, 2), weight=1, uniform="kpi")


        now = _dt.datetime.now()
        self.day_var = tk.StringVar(value=str(now.day))
        self.month_var = tk.StringVar(value=str(now.month))
        self.year_var = tk.StringVar(value=str(now.year))

        self.m_month_var = tk.StringVar(value=str(now.month))
        self.m_year_var = tk.StringVar(value=str(now.year))

  
        self._card_daily = self._make_card(self.body, 0, "Today’s Sales", "#ffd7ea")
        self._build_daily_controls(self._card_daily["control"])

        self._card_month = self._make_card(self.body, 1, "Monthly Sales", "#ffefb3")
        self._build_month_controls(self._card_month["control"])

        self._card_total = self._make_card(self.body, 2, "All-Time Summary", "#ead7ff")


        self.refresh()




    def _make_card(self, parent, col, badge_text, badge_color):
        card = ct.CTkFrame(
            parent, fg_color=WHITE,
            corner_radius=22, border_width=2, border_color="#dedede"
        )
        card.grid(row=0, column=col, sticky="nsew", padx=16, pady=8)
        card.grid_columnconfigure(0, weight=1)

        pill = ct.CTkFrame(card, fg_color=badge_color, corner_radius=20)
        pill.grid(row=0, column=0, sticky="w", padx=22, pady=(16, 0))
        ct.CTkLabel(pill, text=badge_text, font=F(16, "bold"), text_color="black")\
            .pack(padx=14, pady=6)

        inner = ct.CTkFrame(card, fg_color=WHITE)
        inner.grid(row=1, column=0, sticky="nsew", padx=22, pady=12)
        inner.grid_columnconfigure(0, weight=1)

        v1 = tk.StringVar(value="-")
        v2 = tk.StringVar(value="-")
        v3 = tk.StringVar(value="-")

        ct.CTkLabel(inner, text="ยอดขายรวม", font=F(22, "bold"),
                    text_color="black").grid(row=0, column=0, sticky="w", pady=(8,0))

        self._mk_row(inner, "คำสั่งซื้อ", v2, 1)
        self._mk_row(inner, "จำนวนสินค้าที่สั่ง", v3, 2)

        return {
            "frame": card,
            "control": inner,
            "v_total": v1,
            "v_orders": v2,
            "v_items": v3,
        }


    def _mk_row(self, parent, title, var, r):
        row = ct.CTkFrame(parent, fg_color=WHITE)
        row.grid(row=r, column=0, sticky="ew", pady=(10,0))
        row.grid_columnconfigure(0, weight=1)

        ct.CTkLabel(row, text=title, font=F(16), text_color="#444")\
            .grid(row=0, column=0, sticky="w")
        ct.CTkLabel(row, textvariable=var, font=F(20, "bold"),
                    text_color="black").grid(row=1, column=0, sticky="w")



    def _build_daily_controls(self, parent):
        # กรอบควบคุม (ลดลงอีก ~20%)
        ctrl = ct.CTkFrame(parent, fg_color=WHITE)
        ctrl.grid(row=3, column=0, sticky="w", pady=(6, 4))

        days   = [str(i) for i in range(1, 32)]
        months = [str(i) for i in range(1, 13)]
        years  = [str(y) for y in range(2023, 2031)]


        ct.CTkLabel(ctrl, text="Day", font=F(12)).grid(row=0, column=0, padx=(0, 5))
        ct.CTkOptionMenu(
            ctrl, values=days, variable=self.day_var,
            width=58, height=26, fg_color=BLUE_LIGHT,
            button_color=BLUE_DARK, text_color="black", font=F(12)
        ).grid(row=0, column=1, padx=3)

        ct.CTkLabel(ctrl, text="Month", font=F(11)).grid(row=0, column=2, padx=(8, 5))
        ct.CTkOptionMenu(
            ctrl, values=months, variable=self.month_var,
            width=58, height=26, fg_color=BLUE_LIGHT,
            button_color=BLUE_DARK, text_color="black", font=F(12)
        ).grid(row=0, column=3, padx=3)

        ct.CTkLabel(ctrl, text="Year", font=F(11)).grid(row=0, column=4, padx=(8, 5))
        ct.CTkOptionMenu(
            ctrl, values=years, variable=self.year_var,
            width=68, height=26, fg_color=BLUE_LIGHT,
            button_color=BLUE_DARK, text_color="black", font=F(12)
        ).grid(row=0, column=5, padx=3)


        ct.CTkButton(
            ctrl, text="Apply", width=52, height=26,
            fg_color=BLUE_LIGHT, hover_color=BLUE_DARK,
            text_color="black", corner_radius=10, font=F(12, "bold"),
            command=self._calc_daily
        ).grid(row=0, column=6, padx=(10, 0))


    def _build_month_controls(self, parent):
        ctrl = ct.CTkFrame(parent, fg_color=WHITE)
        ctrl.grid(row=3, column=0, sticky="w", pady=(8, 6))

        months = [str(i) for i in range(1, 13)]
        years  = [str(y) for y in range(2023, 2031)]

        ct.CTkLabel(ctrl, text="Month", font=F(12)).grid(row=0, column=0, padx=(0, 6))
        ct.CTkOptionMenu(
            ctrl, values=months, variable=self.m_month_var,
            width=72, height=28, fg_color=BLUE_LIGHT,
            button_color=BLUE_DARK, text_color="black", font=F(12)
        ).grid(row=0, column=1, padx=4)

        ct.CTkLabel(ctrl, text="Year", font=F(12)).grid(row=0, column=2, padx=(10, 6))
        ct.CTkOptionMenu(
            ctrl, values=years, variable=self.m_year_var,
            width=84, height=28, fg_color=BLUE_LIGHT,
            button_color=BLUE_DARK, text_color="black", font=F(12)
        ).grid(row=0, column=3, padx=4)

        ct.CTkButton(
            ctrl, text="Apply", width=64, height=28,
            fg_color=BLUE_LIGHT, hover_color=BLUE_DARK,
            text_color="black", corner_radius=12, font=F(12, "bold"),
            command=self._calc_month
        ).grid(row=0, column=4, padx=(12, 0))



    def refresh(self):
        self._calc_daily()
        self._calc_month()
        self._calc_total()
        self._build_bestsellers() 



    def _calc_daily(self):
        try:
            d = int(self.day_var.get())
            m = int(self.month_var.get())
            y = int(self.year_var.get())
            start = _dt.datetime(y, m, d)
            end = start + _dt.timedelta(days=1)
        except:
            return

        rev, cnt, items = self.app.db.sales_stats(start.isoformat(" "), end.isoformat(" "))
        self._card_daily["v_orders"].set(f"{cnt:,} คำสั่งซื้อ")
        self._card_daily["v_items"].set(f"{items:,} ชิ้น")
        self._show_total_amount(self._card_daily["control"], rev)


    def _calc_month(self):
        try:
            m = int(self.m_month_var.get())
            y = int(self.m_year_var.get())
            start = _dt.datetime(y, m, 1)
            end = _dt.datetime(y+1, 1, 1) if m == 12 else _dt.datetime(y, m+1, 1)
        except:
            return

        rev, cnt, items = self.app.db.sales_stats(start.isoformat(" "), end.isoformat(" "))
        self._card_month["v_orders"].set(f"{cnt:,} คำสั่งซื้อ")
        self._card_month["v_items"].set(f"{items:,} ชิ้น")
        self._show_total_amount(self._card_month["control"], rev)


    def _calc_total(self):
        rev, cnt, items = self.app.db.sales_stats(None, None)
        self._card_total["v_orders"].set(f"{cnt:,} คำสั่งซื้อ (ทั้งหมด)")
        self._card_total["v_items"].set(f"{items:,} ชิ้น (ทั้งหมด)")
        self._show_total_amount(self._card_total["control"], rev)


    def _build_bestsellers(self):
        for w in getattr(self, "_best_widgets", []):
            w.destroy()
        self._best_widgets = []

        title = ct.CTkLabel(
            self.scroll,
            text="Top 5 Bestsellers",
            font=F(36, "bold"),
            text_color="black"
        )
        title.grid(row=2, column=0, sticky="w", padx=50, pady=(30, 10))
        self._best_widgets.append(title)

        wrap = ct.CTkFrame(self.scroll, fg_color=WHITE)
        wrap.grid(row=3, column=0, sticky="nw", padx=50, pady=(0, 50))
        self._best_widgets.append(wrap)


        CARD_W = 230
        CARD_H = 340
        IMG_SIZE = 150

        tops = self.app.db.get_top5_bestsellers()

 
        for i, (pid, name, img_path, sold, price) in enumerate(tops, start=1):

            card = ct.CTkFrame(
                wrap, fg_color=WHITE,
                border_width=1, border_color="#dcdcdc",
                corner_radius=20,
                width=CARD_W, height=CARD_H
            )
            card.grid(row=0, column=i-1, padx=20)
            card.grid_propagate(False)
            card.pack_propagate(False)


            # badge อันดับ
            badge = ct.CTkFrame(card, fg_color="red",
                                width=40, height=40, corner_radius=20)
            badge.place(x=10, y=10)
            ct.CTkLabel(badge, text=str(i),
                        font=F(16, "bold"), text_color="white")\
                        .place(relx=0.5, rely=0.5, anchor="center")

            # รูปสินค้า
            IMG_REAL = int(IMG_SIZE * 1)
            img = image_widget(card, img_path, IMG_REAL, IMG_REAL, corner=16)
            img.pack(pady=(60, 12))


            # ชื่อสินค้า
            ct.CTkLabel(
                card, text=name, wraplength=CARD_W - 60,
                justify="center", font=F(16, "bold"),
                text_color="black"
            ).pack(pady=(0,6))

            ct.CTkLabel(card, text=f"{price:,} บาท",
                        font=F(15), text_color="#555").pack()

            ct.CTkLabel(card, text=f"ขายแล้ว {sold} ชิ้น",
                        font=F(15), text_color="#777").pack()


    def _show_total_amount(self, parent, amount):

        if not hasattr(parent, "_total_row"):
            parent._total_row = ct.CTkFrame(parent, fg_color=WHITE)
            parent._total_row.grid(row=10, column=0, sticky="w",
                                   pady=(16, 6))

            ct.CTkLabel(parent._total_row, text="ยอดขายรวม",
                        font=F(18, "bold"),
                        text_color="#666").grid(row=0, column=0)

            parent._total_val = ct.CTkLabel(
                parent._total_row, text="",
                font=F(22, "bold"), text_color="black"
            )
            parent._total_val.grid(row=0, column=1, padx=(8,0))

        parent._total_val.configure(text=f"{int(amount):,} บาท")



#main app
class App(ct.CTk):
    def __init__(self, left_image_path=None, logo_path=None):
        super().__init__()
        self.title("STAY_ZONE")
        self.configure(fg_color=WHITE)
        self.after(0, self._maximize)

        self.left_image_path = left_image_path
        self.logo_path = logo_path
        self.db = ShopDB()
        self.reset_username = None
        self.current_user = None
        self.cart = {}
        self.is_admin = False

        container = ct.CTkFrame(self, fg_color=WHITE)
        container.pack(fill="both", expand=True)
        
        # สร้างหน้าเพจต่างๆ
        self.pages = {}
        for Cls, name in [
            (SignInPage, "SignIn"),
            (SignUpPage, "SignUp"),
            (ResetRequestPage, "ResetRequest"),
            (ResetSetPage, "ResetSet"),
            (HomePage, "Home"),
            (CartPage, "Cart"),
            (CheckoutPage, "Checkout"),
            (UserProfilePage, "UserProfile"),    
            (UserOrdersPage, "UserOrders"),       
            (AdminDashboardPage, "AdminDashboard"),
            (AdminAddPage, "AdminAdd"),
            (AdminRemovePage, "AdminRemove"),
            (AdminStockPage, "AdminStock"),
            (AdminOrdersPage, "AdminOrders"),
            (AdminAllOrdersPage, "AdminAllOrders"),
            (AdminSummaryPage, "AdminSummary"),
        ]:

            page = Cls(container, self)
            self.pages[name] = page
            page.place(relx=0, rely=0, relwidth=1, relheight=1)

      
        self.show("SignIn")

        
        
    #Helpers for TopBar/Profile
    def get_current_user_info(self):

        u = getattr(self, "current_user", None)
        if not u:
            return None
        self.db.c.execute("SELECT username, email, IFNULL(profile_image,'') FROM users WHERE username=?", (u,))
        return self.db.c.fetchone()

    def get_current_avatar_ctkimage(self, size=44):
  
        try:
            row = self.get_current_user_info()
            p = row[2] if row else None
            if p and os.path.exists(p):
                im = Image.open(p).convert("RGBA")
            else:
                
                p2 = getattr(self, "app_image_path", None)
                im = Image.open(p2).convert("RGBA") if (p2 and os.path.exists(p2)) \
                     else Image.new("RGBA", (size, size), (230,230,230,255))
            im = ImageOps.fit(im, (size, size), Image.LANCZOS)
            mask = Image.new("L", (size, size), 0)
            ImageDraw.Draw(mask).ellipse((0, 0, size-1, size-1), fill=255)
            im.putalpha(mask)
            return CTkImage(light_image=im, size=(size, size))
        except Exception:
            ph = Image.new("RGBA", (size, size), (230,230,230,255))
            return CTkImage(light_image=ph, size=(size, size))



    # ขยายหน้าต่างเต็มจอ
    def _maximize(self):
        try: self.state("zoomed")
        except: pass
        self.update_idletasks()
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f"{sw}x{sh}+0+0")

    # แสดงหน้าเพจ
 
    def show(self, name):
        if name not in self.pages:
            return
        frame = self.pages[name]
        frame.tkraise()

        
        if hasattr(frame, "refresh"):
            try:
                frame.refresh()
            except Exception:
                pass

        
        self.refresh_all_topbars()


        if hasattr(frame, "refresh"):
            try:
                frame.refresh()
            except Exception:
                pass


        if name == "UserProfile" and hasattr(self.pages["UserProfile"], "refresh"):
            self.pages["UserProfile"].refresh()
        if name == "UserOrders" and hasattr(self.pages["UserOrders"], "refresh"):
            self.pages["UserOrders"].refresh()






        # รีเซ็ตฟอร์มเพิ่มสินค้า
        if name == "AdminAdd":
            try:
                self.pages["AdminAdd"].reset_form()
            except Exception:
                pass

        self.pages[name].tkraise()


    # ออกจากระบบ
    def logout(self):

        self.current_user = None
        self.cart.clear()
        self.is_admin = False

        # รีเซ็ตฟอร์มหน้า sign in / sign up
        try: self.pages["SignIn"].reset()
        except Exception: pass
        try: self.pages["SignUp"].reset()
        except Exception: pass

        messagebox.showinfo("Logout", "ออกจากระบบแล้ว")
        self.show("SignIn")

    # ไปหน้าcheckout
    def goto_checkout(self):
        chk = self.pages["Checkout"]
        chk.populate()
        self.show("Checkout")
        
        
        
    def refresh_all_topbars(self):
        try:
            for page in self.pages.values():
                for ch in page.winfo_children():
                    if isinstance(ch, TopBar):
                        ch.refresh_avatar()
        except Exception:
            pass




#run app
if __name__ == "__main__":
    Billboard_PATH = r"C:/Users/suphi/OneDrive/Desktop/project/photo/Billboard.jpg"
    LOGO_PATH  = r"C:/Users/suphi/OneDrive/Desktop/project/photo/logo.jpg"
    app = App(
        left_image_path=Billboard_PATH if os.path.exists(Billboard_PATH) else None,
        logo_path=LOGO_PATH if os.path.exists(LOGO_PATH) else None
    )
    # qr
    app.app_image_path = r"C:/Users/suphi/OneDrive/Desktop/project/photo/qr.png"
    app.mainloop()
