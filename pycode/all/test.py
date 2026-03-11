import os, re, sqlite3
import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog
import customtkinter as ct
from PIL import Image, ImageTk, ImageOps, ImageDraw
import tkinter.ttk as ttk


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


#๊ui 

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



    # ----- users -----
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

    # ----- products -----
    def list_products(self):
        self.c.execute("SELECT id,name,price,stock,image_path FROM products ORDER BY id ASC")
        return self.c.fetchall()

    def get_product(self, product_id):
        self.c.execute("SELECT id,name,price,stock,image_path FROM products WHERE id=?", (product_id,))
        return self.c.fetchone()

    def add_product(self, name: str, price: int, stock: int, image_path: str|None):
        self.c.execute("INSERT INTO products(name,price,stock,image_path) VALUES (?,?,?,?)",
                       (name, int(price), int(stock), image_path))
        self.conn.commit()

    def update_product(self, product_id: int, *, stock: int|None=None, price: int|None=None):
        if stock is not None:
            self.c.execute("UPDATE products SET stock=? WHERE id=?", (int(stock), product_id))
        if price is not None:
            self.c.execute("UPDATE products SET price=? WHERE id=?", (int(price), product_id))
        self.conn.commit()

    def delete_product(self, product_id: int):
        self.c.execute("DELETE FROM products WHERE id=?", (product_id,))
        self.conn.commit()

    def list_products_full(self):
        self.c.execute("SELECT id,name,stock,price,image_path FROM products ORDER BY id ASC")
        return self.c.fetchall()

    # ----- orders -----
    def generate_order_id(self):
        import random
        while True:
            code = f"TH{random.randint(1000,9999)}-{random.randint(10,99)}"
            self.c.execute("SELECT 1 FROM orders WHERE order_id=?", (code,))
            if not self.c.fetchone():
                return code

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

        # บันทึกรายการย่อย + หักสต๊อก
        for pid, qty in cart_items:
            self.c.execute("SELECT name, price, stock FROM products WHERE id=?", (pid,))
            row = self.c.fetchone()
            if not row:
                continue
            name, price, stock = row
            sub = int(price) * int(qty)
            self.c.execute("""
                INSERT INTO order_items(order_id, product_id, product_name, qty, price_each, sub_total)
                VALUES (?,?,?,?,?,?)
            """, (order_id, pid, name, int(qty), int(price), sub))
            self.c.execute("UPDATE products SET stock = MAX(stock - ?, 0) WHERE id=?", (int(qty), pid))

        self.conn.commit()
        return order_id, total

    def list_orders(self):
        self.c.execute("""
            SELECT order_id, customer_name, phone, address, total, created_at, payment_image
            FROM orders ORDER BY id DESC
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



# ---------- UI Helpers ----------
def entry_box(master, placeholder: str, show_char=None):
    """อินพุตสวย ๆ ใช้ซ้ำ"""
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
        seg = segmented(right, on_switch=lambda v: app.show("SignUp") if v=="Sign up" else None)
        seg.set("Sign in")
        seg.grid(row=1, column=0, pady=(0, 50), sticky="n")


        # ฟอร์มเข้าสู่ระบบ
        form = half_form(right, top_offset=0.38)
        ct.CTkLabel(form, text="Username", font=F(14), text_color="black", anchor="w").grid(row=0, column=0, sticky="w")
        self.username = entry_box(form, "Enter your username"); self.username.grid(row=1, column=0, pady=(0,8), sticky="ew")
        ct.CTkLabel(form, text="Password", font=F(14), text_color="black", anchor="w").grid(row=2, column=0, sticky="w")
        self.password = entry_box(form, "Enter your password", show_char="•"); self.password.grid(row=3, column=0, pady=(0,8), sticky="ew")


        # ปุ่มลืมรหัสผ่าน
        ct.CTkButton(form, text="Forgot password?", fg_color="transparent", hover=False,
                     text_color=BLUE_DARK, command=lambda: app.show("ResetRequest"), font=F(13))\
            .grid(row=4, column=0, sticky="e", pady=(0,6))


        # ปุ่ม Sign in
        primary_btn(form, "Login", self.do_login).grid(row=5, column=0, sticky="ew", pady=(6,8))  # #ปุ่ม Sign in

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
        seg = segmented(right, on_switch=lambda v: app.show("SignIn") if v == "Sign in" else None)
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
        draw = ImageDraw.Draw(ph)
        draw.ellipse((0, 0, AVATAR-1, AVATAR-1), fill=(235, 235, 235, 255))
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

        ct.CTkLabel(form, text="Username", font=F(14), text_color="black", anchor="w").grid(row=0, column=0, sticky="w")
        self.username = entry_box(form, "อย่างน้อย 6 ตัวอักษร"); self.username.configure(width=ENTRY_W)
        self.username.grid(row=1, column=0, pady=(0,8), sticky="w")

        ct.CTkLabel(form, text="Email", font=F(14), text_color="black", anchor="w").grid(row=2, column=0, sticky="w")
        self.email = entry_box(form, "your@email.com"); self.email.configure(width=ENTRY_W)
        self.email.grid(row=3, column=0, pady=(0,8), sticky="w")

        ct.CTkLabel(form, text="Password", font=F(14), text_color="black", anchor="w").grid(row=4, column=0, sticky="w")
        self.password = entry_box(form, "อย่างน้อย 8 ตัวอักษร", show_char="•"); self.password.configure(width=ENTRY_W)
        self.password.grid(row=5, column=0, pady=(0,8), sticky="w")

        ct.CTkLabel(form, text="Confirm Password", font=F(14), text_color="black", anchor="w").grid(row=6, column=0, sticky="w")
        self.cpassword = entry_box(form, "พิมพ์รหัสผ่านอีกครั้ง", show_char="•"); self.cpassword.configure(width=ENTRY_W)
        self.cpassword.grid(row=7, column=0, pady=(0,10), sticky="w")

        # ปุ่มสมัคร
        btn_signup = primary_btn(form, "Sign Up", self.do_register)  # #ปุ่ม Sign up
        btn_signup.configure(width=ENTRY_W, height=44, corner_radius=18)
        btn_signup.grid(row=8, column=0, pady=(10, 8), sticky="w")

    def do_register(self):
        u, email, pw, cpw = (
            self.username.get().strip(),
            self.email.get().strip(),
            self.password.get(),
            self.cpassword.get(),
        )

        # ต้องกรอกครบทุกช่องก่อนถึงจะสมัครได้
        if not u or not email or not pw or not cpw:
            messagebox.showwarning("Register", "กรุณากรอกข้อมูลให้ครบทุกช่องก่อนสมัคร")
            return

        # ต้องอัปโหลดรูปโปรไฟล์ด้วย
        if not self.profile_path:
            messagebox.showwarning("Register", "กรุณาอัปโหลดรูปโปรไฟล์ก่อนสมัคร")
            return

        # เงื่อนไขเพิ่มเติม
        if len(u) < 6:
            messagebox.showwarning("Register", "Username อย่างน้อย 6 ตัวอักษร")
            return
        if len(pw) < 8:
            messagebox.showwarning("Register", "Password อย่างน้อย 8 ตัวอักษร")
            return
        if pw != cpw:
            messagebox.showwarning("Register", "รหัสผ่านไม่ตรงกัน")
            return
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            messagebox.showwarning("Register", "รูปแบบอีเมลไม่ถูกต้อง")
            return
        if self.app.db.username_in_use(u):
            messagebox.showerror("Register", "Username นี้ถูกใช้แล้ว")
            return
        if self.app.db.email_in_use(email):
            messagebox.showerror("Register", "อีเมลนี้ถูกใช้งานแล้ว")
            return

        # เซฟไฟล์โปรไฟล์ 
        save_path = None
        if self.profile_path:
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
        draw = ImageDraw.Draw(ph)
        draw.ellipse((0, 0, AVATAR-1, AVATAR-1), fill=(235, 235, 235, 255))
        self._preview_imgtk = ImageTk.PhotoImage(ph)
        self.avatar_holder.configure(image=self._preview_imgtk, text="ยังไม่มี\nรูปภาพ")
        self.avatar_holder.image = self._preview_imgtk


# ลืมรหัสผ่าน - ขอรีเซ็ตรหัส
class ResetRequestPage(ct.CTkFrame):
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
                    text_color="black").grid(row=1, column=0, pady=(180,10))

        form = half_form(right, top_offset=0.38)
        ct.CTkLabel(form, text="Username", font=F(14), text_color="black", anchor="w").grid(row=0, column=0, sticky="w")
        self.username = entry_box(form, "Enter your username"); self.username.grid(row=1, column=0, pady=(0,8), sticky="ew")
        ct.CTkLabel(form, text="Email", font=F(14), text_color="black", anchor="w").grid(row=2, column=0, sticky="w")
        self.email = entry_box(form, "Enter your email"); self.email.grid(row=3, column=0, pady=(0,8), sticky="ew")

        # ปุ่มยืนยันขอตั้งรหัสใหม่
        primary_btn(form, "Continue", self.verify).grid(row=4, column=0, sticky="ew", pady=(10,8))


    def verify(self):
        u, e = self.username.get().strip(), self.email.get().strip()
        if not u or not e: messagebox.showwarning("Reset", "กรอกข้อมูลให้ครบ"); return
        if not self.app.db.match_user_email(u, e):
            messagebox.showerror("Reset", "Username/Email ไม่ตรงกัน"); return
        self.app.reset_username = u
        self.app.show("ResetSet")

# ตั้งรหัสผ่านใหม่
class ResetSetPage(ct.CTkFrame):
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
                    text_color="black").grid(row=0, column=0, pady=(0,10))

        form = half_form(right, top_offset=0.28)
        ct.CTkLabel(form, text="New Password", font=F(14), text_color="black", anchor="w").grid(row=0, column=0, sticky="w")
        self.npw = entry_box(form, "Enter new password", show_char="•"); self.npw.grid(row=1, column=0, pady=(0,8), sticky="ew")
        ct.CTkLabel(form, text="Confirm New Password", font=F(14), text_color="black", anchor="w").grid(row=2, column=0, sticky="w")
        self.cpw = entry_box(form, "Confirm new password", show_char="•"); self.cpw.grid(row=3, column=0, pady=(0,8), sticky="ew")

        # ปุ่ม Submit ตั้งรหัส
        primary_btn(form, "Submit", self.set_pw).grid(row=4, column=0, sticky="ew", pady=(10,8))

    def set_pw(self):
        u = self.app.reset_username
        if not u:
            messagebox.showwarning("Reset", "ทำขั้นตอนก่อนหน้าให้ครบก่อน"); self.app.show("ResetRequest"); return
        pw, cpw = self.npw.get(), self.cpw.get()
        if len(pw) < 8: messagebox.showwarning("Reset", "รหัสผ่านอย่างน้อย 8 ตัวอักษร"); return
        if pw != cpw:   messagebox.showwarning("Reset", "รหัสผ่านไม่ตรงกัน"); return
        ok, msg = self.app.db.set_new_password(u, pw)
        messagebox.showinfo("Reset", msg)
        if ok: self.app.show("SignIn")


# topbar ผู้ใช้
class TopBar(ct.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color=WHITE)
        self.app = app
        self.grid_columnconfigure(0, weight=1)

        left = ct.CTkFrame(self, fg_color=WHITE)
        left.grid(row=0, column=0, sticky="w", padx=36, pady=8)
        logo_box = image_widget(left, getattr(app, "logo_path", None), 100, 100, corner=12)
        logo_box.grid(row=0, column=0, sticky="w")

        btns = ct.CTkFrame(self, fg_color=WHITE)
        btns.grid(row=0, column=1, sticky="e", padx=36)

        # ปุ่มบนtopbar
        nav_btn(btns, "Home", lambda: self.app.show("Home")).grid(row=0, column=0, padx=10)
        nav_btn(btns, "Shopping Cart", lambda: self.app.show("Cart")).grid(row=0, column=1, padx=10)
        nav_btn(btns, "Log out", self.app.logout, primary=True).grid(row=0, column=2, padx=10)


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
        self.content.grid_columnconfigure(0, weight=1)  # spacer
        self.content.grid_columnconfigure(1, weight=5)  # list
        self.content.grid_columnconfigure(2, weight=3)  # summary

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


#checkout
class CheckoutPage(ct.CTkFrame):
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

    # หน้า checkout
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
                    text_color="black", font=F(36, "bold")
                    ).pack(anchor="w", pady=(0,8))

        row = ct.CTkFrame(up_wrap, fg_color=WHITE)
        row.pack(fill="x")

        self.upload_box = ct.CTkFrame(
            row, fg_color=WHITE, corner_radius=12, width=300, height=300
        )
        self.upload_box.grid(row=0, column=0, sticky="w", padx=(0,20), pady=(4,12))
        self.upload_box.grid_propagate(False)

        right = ct.CTkFrame(row, fg_color=WHITE)
        right.grid(row=0, column=1, sticky="w")

        # ปุ่มอัปโหลดหลักฐาน
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
        self.user_preview_label = tk.Label(preview, bg=WHITE, bd=0,
                                           highlightthickness=0, text="ไม่มีรูปภาพ")
        self.user_preview_label.place(relx=0.5, rely=0.5, anchor="center")

        # ฟอร์มที่อยู่จัดส่ง
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

        # ปุ่มบันทึกออเดอร์
        primary_btn(self.body, "บันทึก", self._save_checkout)\
            .pack(anchor="center", pady=(16, 30))  # #ปุ่มบันทึก Checkout

    # บันทึกคำสั่งซื้อ
    def populate(self):
        self._load_system_image()
        for w in self.summary_frame.winfo_children(): w.destroy()

        head = ct.CTkFrame(self.summary_frame, fg_color=WHITE)
        head.pack(fill="x", padx=18, pady=(14,6))
        ct.CTkLabel(head, text="รายการคำสั่งซื้อ:",
                    font=F(25, "bold"),
                    text_color="black").pack(anchor="w")

        table = ct.CTkFrame(self.summary_frame, fg_color=WHITE)
        table.pack(fill="x", padx=18, pady=(0,12))
        table.grid_columnconfigure(0, weight=3)
        table.grid_columnconfigure(1, weight=1)
        table.grid_columnconfigure(2, weight=1)
        table.grid_columnconfigure(3, weight=1)

        hdr_font = F(16, "bold")
        ct.CTkLabel(table, text="ชื่อสินค้า", text_color="#444", font=hdr_font)\
            .grid(row=0, column=0, sticky="w", padx=(6,6))
        ct.CTkLabel(table, text="จำนวน", text_color="#444", font=hdr_font)\
            .grid(row=0, column=1, sticky="e", padx=(6,6))
        ct.CTkLabel(table, text="ราคา", text_color="#444", font=hdr_font)\
            .grid(row=0, column=2, sticky="e", padx=(6,6))
        ct.CTkLabel(table, text="รวม", text_color="#444", font=hdr_font)\
            .grid(row=0, column=3, sticky="e", padx=(6,6))

        ct.CTkFrame(table, height=1, fg_color="#e5e5e5")\
            .grid(row=1, column=0, columnspan=4, sticky="ew", pady=(6,8))

        # แสดงรายการสินค้าในตะกร้า
        total, r = 0, 2
        for pid, qty in self.app.cart.items():
            rec = self.app.db.get_product(pid)
            if not rec: continue
            if len(rec) == 4:
                _id, name, price, _stock = rec
            else:
                _id, name, price, _stock, _img = rec

            sub = int(price) * int(qty); total += sub
            ct.CTkLabel(table, text=name, text_color="black",font=F(16))\
                .grid(row=r, column=0, sticky="w", padx=(6,6))
            ct.CTkLabel(table, text=str(qty), text_color="black",font=F(16))\
                .grid(row=r, column=1, sticky="e", padx=(6,6))
            ct.CTkLabel(table, text=f"{int(price):,} บาท", text_color="black",font=F(16))\
                .grid(row=r, column=2, sticky="e", padx=(6,6))
            ct.CTkLabel(table, text=f"{sub:,} บาท", text_color="black", font=F(16))\
                .grid(row=r, column=3, sticky="e", padx=(6,6))
            r += 1

        ct.CTkFrame(table, height=1, fg_color="#e5e5e5")\
            .grid(row=r, column=0, columnspan=4, sticky="ew", pady=(8,6))
        r += 1
        ct.CTkLabel(table, text="รวมทั้งหมด", font=F(20, "bold"),
                    text_color="black").grid(row=r, column=2, sticky="e", padx=(6,6))
        ct.CTkLabel(table, text=f"{total:,} บาท", font=F(20, "bold"),
                    text_color="black").grid(row=r, column=3, sticky="e", padx=(6,6))

        self.total_var.set(f"{total:,} บาท")

    # โหลดรูปภาพระบบ
    def _load_system_image(self):
        for w in self.upload_box.winfo_children(): w.destroy()
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
                return
            except Exception:
                pass

    # ตรวจสอบหมายเลขโทรศัพท์
    def _validate_phone(self, new_text: str) -> bool:
        if new_text == "":
            return True
        return new_text.isdigit() and len(new_text) <= 10


    # เลือกรูปภาพหลักฐาน
    def _pick_image(self):
        path = filedialog.askopenfilename(
            title="เลือกไฟล์รูปภาพ",
            filetypes=[("Image files","*.png;*.jpg;*.jpeg;*.webp;*.bmp")]
        )
        if not path: return
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

    # บันทึกคำสั่งซื้อ
    def _save_checkout(self):
        name  = self.name_entry.get().strip()
        phone = self.phone_entry.get().strip()
        addr  = self.addr_entry.get().strip()
        if not name or not phone or not addr:
            messagebox.showwarning("Checkout",  "กรอกข้อมูลที่อยู่ให้ครบ")
            return
        if not self.app.cart:
            messagebox.showwarning("Checkout", "ตะกร้าว่างเปล่า")
            return

        # บันทึกออเดอร์ลงฐานข้อมูล
        cart_items = list(self.app.cart.items())  # [(pid, qty), ...]
        order_id, total = self.app.db.create_order(
            self.app.current_user or "guest",
            name, phone, addr,
            cart_items
        )

        # บันทึกรูปภาพ
        save_path = None
        if self.upload_path:
            try:
                pay_dir = os.path.join(os.path.dirname(DB_PATH), "payments")
                os.makedirs(pay_dir, exist_ok=True)
                ext = os.path.splitext(self.upload_path)[1].lower() or ".png"

                # ตั้งชื่อไฟล์ตาม ORDER ID 
                save_path = os.path.join(pay_dir, f"{order_id}{ext}")

                img = Image.open(self.upload_path)
                if img.mode not in ("RGB", "RGBA"):
                    img = img.convert("RGB")
                img.save(save_path)

                # อัปเดตพาธรูปในตาราง orders
                self.app.db.c.execute(
                    "UPDATE orders SET payment_image=? WHERE order_id=?",
                    (save_path, order_id)
                )
                self.app.db.conn.commit()
            except Exception as e:
                save_path = None
                messagebox.showwarning("Checkout", f"บันทึกรูปไม่สำเร็จ (ยังสร้างออเดอร์แล้ว)\n{e}")

        # แสดงข้อความยืนยัน
        msg = f"บันทึกออเดอร์สำเร็จ\nORDER ID: {order_id}\nยอดรวม    {total:,} บาท"
        if save_path:
            msg += f"\n(แนบรูป: {os.path.basename(save_path)})"
        messagebox.showinfo("Checkout", msg)

        # เคลียร์ตะกร้าและกลับสู่ home
        self.app.cart.clear()
        self.app.show("Home")



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

        # ปุ่มบน top bar
        nav_btn(btns, "Dashboard", lambda: app.show("AdminDashboard")).grid(row=0, column=0, padx=10)
        nav_btn(btns, "Add",       lambda: app.show("AdminAdd")).grid(row=0, column=1, padx=10)
        nav_btn(btns, "Remove",    lambda: app.show("AdminRemove")).grid(row=0, column=2, padx=10)
        nav_btn(btns, "Order",     lambda: app.show("AdminOrders")).grid(row=0, column=3, padx=10)
        nav_btn(btns, "Log out",   lambda: app.logout(), primary=True).grid(row=0, column=4, padx=10)



#dashboard
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

        self.render()

    def render(self):
        # ลบของเก่า
        for w in self.body.winfo_children():
            w.destroy()

        products = self.app.db.list_products()

        grid = ct.CTkFrame(self.body, fg_color=WHITE)
        grid.pack(fill="x", expand=True)

        # ปรับระยะขอบ
        sw = max(1, self.winfo_screenwidth())
        gutter = int(sw * 0.10)
        grid.pack_configure(padx=(gutter, gutter))

        COLS = 4
        IMG_W, IMG_H = 260, 260
        CARD_W = IMG_W + 40
        CARD_H = IMG_H + 120

        for i in range(COLS):
            grid.grid_columnconfigure(i, weight=1, uniform="acol")

        if not products:
            ct.CTkLabel(self.body, text="ยังไม่มีสินค้าในฐานข้อมูล",
                        text_color="black", font=F(18)).pack(pady=30)
            return

        for idx, rec in enumerate(products):
            if len(rec) == 4:
                pid, name, price, stock = rec
                img_path = None
            else:
                pid, name, price, stock, img_path = rec

            r, c = divmod(idx, COLS)

            card = ct.CTkFrame(
                grid,
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

            # #ชื่อสินค้า 
            ct.CTkLabel(
                meta,
                text=name,
                text_color="black",
                font=F(14, "bold"),
                justify="left",     
                wraplength=180      
            ).grid(row=0, column=0, sticky="w")

            ct.CTkLabel(meta, text=f"สต๊อก {int(stock):,} ชิ้น", text_color="#666", font=F(12))\
                .grid(row=0, column=1, sticky="e")
            ct.CTkLabel(meta, text=f"{int(price):,} บาท", text_color="#333", font=F(14))\
                .grid(row=1, column=0, sticky="w", pady=(2, 0))



#add
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

        # รีเซ็ตฟอร์ม
        self.reset_form()

        # กลับหน้าแดชบอร์ด
        self.app.show("AdminDashboard")

          
        


#remove
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
        self.tree.column("stock", width=180, anchor="center")
        self.tree.column("price", width=160, anchor="e")

        self.tree.grid(row=0, column=0, sticky="nsew")

        self.refresh_table()

        btn_frame = ct.CTkFrame(self, fg_color=WHITE)
        btn_frame.grid(row=3, column=0, pady=(0, 40))

        primary_btn(btn_frame, "เพิ่มจำนวน", self.increase_stock).pack(pady=8)  # #ปุ่มเพิ่มจำนวน
        primary_btn(btn_frame, "ลดจำนวน", self.decrease_stock).pack(pady=8)    # #ปุ่มลดจำนวน
        primary_btn(btn_frame, "แก้ไขราคา", self.edit_price).pack(pady=8)      # #ปุ่มแก้ราคา
        primary_btn(btn_frame, "ลบสินค้า", self.remove_item).pack(pady=8)      # #ปุ่มลบสินค้า

    # รีเฟรชตารางสินค้า
    def refresh_table(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        for row in self.app.db.list_products():
            if len(row) == 4:
                pid, name, price, stock = row
            else:
                pid, name, price, stock, _ = row
            self.tree.insert("", "end", values=(pid, name, stock, price))
    
    def refresh(self):
        self.refresh_table()
    # เพิ่มจำนวนสินค้า
    def increase_stock(self):
        self._change_stock(delta=1)

    # ลดจำนวนสินค้า
    def decrease_stock(self):
        self._change_stock(delta=-1)

    # แก้ไขราคาสินค้า
    def edit_price(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("เลือกสินค้า", "กรุณาเลือกสินค้าที่ต้องการแก้ราคา")
            return
        item = self.tree.item(sel[0])
        pid, name, stock, price = item["values"]
        new_price = simpledialog.askinteger("แก้ไขราคา", f"ราคาปัจจุบัน {price} บาท\nกรอกราคาที่ต้องการใหม่:")
        if new_price is not None:
            self.app.db.c.execute("UPDATE products SET price=? WHERE id=?", (new_price, pid))
            self.app.db.conn.commit()
            messagebox.showinfo("สำเร็จ", f"อัปเดตราคาของ {name} เป็น {new_price:,} บาทแล้ว")
            self.refresh_table()

    # ลบสินค้า
    def remove_item(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("ลบสินค้า", "กรุณาเลือกสินค้าที่ต้องการลบ")
            return
        item = self.tree.item(sel[0])
        pid, name, *_ = item["values"]
        if messagebox.askyesno("ยืนยันการลบ", f"ต้องการลบ {name} ใช่หรือไม่?"):
            self.app.db.c.execute("DELETE FROM products WHERE id=?", (pid,))
            self.app.db.conn.commit()
            messagebox.showinfo("ลบสำเร็จ", f"ลบ {name} แล้ว")
            self.refresh_table()

    # เปลี่ยนแปลงสต๊อกสินค้า
    def _change_stock(self, delta):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("ปรับจำนวน", "กรุณาเลือกสินค้า")
            return
        item = self.tree.item(sel[0])
        pid, name, stock, price = item["values"]
        new_stock = max(0, int(stock) + delta)
        self.app.db.c.execute("UPDATE products SET stock=? WHERE id=?", (new_stock, pid))
        self.app.db.conn.commit()
        self.refresh_table()


# orders
class AdminOrdersPage(ct.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color=WHITE)
        self.app = app

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        AdminTopBar(self, app).grid(row=0, column=0, sticky="ew")

        title = ct.CTkLabel(self, text="Orders", font=F(36, "bold"), text_color="black")
        title.grid(row=1, column=0, sticky="w", padx=50, pady=(6, 0))

        self.body = ct.CTkScrollableFrame(self, fg_color=WHITE)
        self.body.grid(row=2, column=0, sticky="nsew", padx=40, pady=10)
        hide_scrollbar(self.body)

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

            # การ์ดคำสั่งซื้อ
            card = ct.CTkFrame(self.body, fg_color=WHITE, corner_radius=18,
                            border_width=1, border_color="#dedede")
            card.pack(fill="x", padx=10, pady=14)
            
            # การ์ดด้านใน
            inner = ct.CTkFrame(card, fg_color=WHITE)
            inner.pack(fill="both", padx=22, pady=20)

            # กรอบพรีวิวหลักฐานการชำระเงิน
            proof = ct.CTkFrame(inner, fg_color=WHITE)
            proof.place(relx=0.93, rely=0.05, anchor="ne") 

            ct.CTkLabel(proof, text="หลักฐานการชำระเงิน",
                        font=F(20, "bold"), text_color="black")\
            .pack(anchor="e", pady=(0, 6))

            PROOF_W, PROOF_H = 150, 150  # ขนาดกรอบพรีวิวหลักฐาน
            proof_box = ct.CTkFrame(
                proof, fg_color=WHITE, border_width=1, border_color="#e5e5e5",
                corner_radius=12, width=PROOF_W, height=PROOF_H
            )
            proof_box.pack()
            proof_box.grid_propagate(False)

            # โหลดและแสดงรูปภาพหลักฐานการชำระเงิน
            try:
                if pay_img and os.path.exists(pay_img):
                    img = Image.open(pay_img)
                    img_ratio  = img.width / img.height
                    box_ratio  = PROOF_W / PROOF_H
                    
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
                    tk.Label(proof_box, text="ไม่มีรูป", bg=WHITE)\
                    .place(relx=0.5, rely=0.5, anchor="center")
            except Exception:
                tk.Label(proof_box, text="ไม่มีรูป", bg=WHITE)\
                .place(relx=0.5, rely=0.5, anchor="center")

            # order id header
            hdr = ct.CTkFrame(inner, fg_color=BLUE_LIGHT, corner_radius=20)
            hdr.pack(anchor="w", pady=(0, 12))
            ct.CTkLabel(hdr, text=f"ORDER ID:  {order_id}", font=F(28, "bold"),
                        text_color="black").pack(padx=16, pady=10)

            # ข้อมูลลูกค้า
            info = ct.CTkFrame(inner, fg_color=WHITE)
            info.pack(anchor="w", pady=(7, 9))
            ct.CTkLabel(info, text=f"ชื่อ :  {cname}",    font=F(15), text_color="black").grid(row=0, column=0, sticky="w", pady=(0,4))
            ct.CTkLabel(info, text=f"เบอร์โทร :  {phone}", font=F(15), text_color="black").grid(row=1, column=0, sticky="w", pady=(0,4))
            ct.CTkLabel(info, text=f"ที่อยู่ :  {addr}",   font=F(15), text_color="black").grid(row=2, column=0, sticky="w")

            # หัวข้อคำสั่งซื้อ
            ct.CTkLabel(inner, text="คำสั่งซื้อ", font=F(22, "bold"), text_color="black")\
                .pack(anchor="w", pady=(8, 7))

            # ตารางรายการสินค้า
            table = ct.CTkFrame(inner, fg_color=WHITE)
            table.pack(fill="x")
            table.grid_columnconfigure(0, weight=4)
            table.grid_columnconfigure(1, weight=1)
            table.grid_columnconfigure(2, weight=1)

            hdrf = F(16, "bold")
            ct.CTkLabel(table, text="ชื่อสินค้า",   font=hdrf, text_color="black").grid(row=0, column=0, sticky="w")
            ct.CTkLabel(table, text="จำนวนที่สั่ง", font=hdrf, text_color="black").grid(row=0, column=1, sticky="e")
            ct.CTkLabel(table, text="ราคา",       font=hdrf, text_color="black").grid(row=0, column=2, sticky="e")
            
            ct.CTkFrame(table, height=1, fg_color="#e5e5e5")\
                .grid(row=1, column=0, columnspan=3, sticky="ew", pady=(7,9))

            # รายการสินค้า
            r = 2
            for pname, qty, price_each, sub_total in self.app.db.get_order_items(order_id):
                ct.CTkLabel(table, text=pname, font=F(16), text_color="black")\
                    .grid(row=r, column=0, sticky="w", pady=3)
                ct.CTkLabel(table, text=str(qty), font=F(16), text_color="black")\
                    .grid(row=r, column=1, sticky="e", pady=3)
                ct.CTkLabel(table, text=f"{sub_total:,} บาท", font=F(16), text_color="black")\
                    .grid(row=r, column=2, sticky="e", pady=3)
                r += 1
            
            ct.CTkFrame(table, height=1, fg_color="#e5e5e5")\
                .grid(row=r, column=0, columnspan=3, sticky="ew", pady=(9,9))   
            r += 1
            ct.CTkLabel(table, text="ราคารวมทั้งหมด", font=F(19, "bold"), text_color="black")\
                .grid(row=r, column=1, sticky="e")
            ct.CTkLabel(table, text=f"{int(total):,} บาท", font=F(19, "bold"), text_color="black")\
                .grid(row=r, column=2, sticky="e")

            # ปุ่ม mark as done
            ct.CTkButton(inner, text="Mark as Done", width=160,
                        fg_color=BLUE_LIGHT, hover_color=BLUE_DARK, text_color="black",
                        font=F(18),
                        command=lambda oid=order_id, c=card: self._done(oid, c))\
                .pack(pady=(17, 7))  

    # ปิดงานออเดอร์
    def _done(self, oid, card_widget):
        if messagebox.askyesno("ยืนยัน", f"ปิดงานออเดอร์ {oid} ?"):
            self.app.db.delete_order(oid)
            try:
                card_widget.destroy()
            except Exception:
                pass



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
            (AdminDashboardPage, "AdminDashboard"),
            (AdminAddPage, "AdminAdd"),
            (AdminRemovePage, "AdminRemove"),
            (AdminOrdersPage, "AdminOrders"),
        ]:
            page = Cls(container, self)
            self.pages[name] = page
            page.place(relx=0, rely=0, relwidth=1, relheight=1)

        self.show("SignIn")

    # ขยายหน้าต่างเต็มจอ
    def _maximize(self):
        try: self.state("zoomed")
        except: pass
        self.update_idletasks()
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f"{sw}x{sh}+0+0")

    # แสดงหน้าเพจ
    def show(self, name):
        if name.startswith("Admin") and not self.is_admin:
            name = "Home"
        if name in ("Home", "Cart", "Checkout") and self.is_admin:
            name = "AdminDashboard"

        #รีเฟรชหน้า
        if name == "Cart":
            self.pages["Cart"].refresh()
        if name == "Home":
            self.pages["Home"].render_products()
        if name == "AdminDashboard":
            self.pages["AdminDashboard"].render()
        if name == "AdminRemove":
            self.pages["AdminRemove"].refresh_table()
        if name == "AdminOrders":
            self.pages["AdminOrders"].refresh()

        # รีเซ็ตฟอร์มเพิ่มสินค้า
        if name == "AdminAdd":
            try:
                self.pages["AdminAdd"].reset_form()
            except Exception:
                pass

        self.pages[name].tkraise()


    # ออกจากระบบ
    def logout(self):
        """ออกจากระบบ และรีเซ็ตฟอร์ม"""
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
