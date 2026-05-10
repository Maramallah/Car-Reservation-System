# ============================================================
#  CAR RENTAL SYSTEM — Tkinter Desktop App
#  Alexandria National University — DB Final Project 2026
#  Requires: pip install pyodbc
# ============================================================

import tkinter as tk
from tkinter import ttk, messagebox
import pyodbc

# ─────────────────────────────────────────
#  DATABASE CONNECTION
# ─────────────────────────────────────────
SERVER   = "localhost\\SQLEXPRESS"
DATABASE = "CarRentalSystem"

def get_connection():
    conn_str = (
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={SERVER};"
        f"DATABASE={DATABASE};"
        f"Trusted_Connection=yes;"
    )
    return pyodbc.connect(conn_str)

def call_proc(proc_name, params=()):
    """Call a stored procedure and return (columns, rows) or ([], [])."""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        placeholders = ",".join(["?" for _ in params])
        cursor.execute(f"EXEC {proc_name} {placeholders}", params)
        try:
            rows    = cursor.fetchall()
            columns = [d[0] for d in cursor.description]
            conn.commit()
            return columns, rows
        except pyodbc.ProgrammingError:
            conn.commit()
            return [], []
    except Exception as e:
        messagebox.showerror("Database Error", str(e))
        return None, None
    finally:
        if conn:
            conn.close()

def run_query(sql, params=()):
    """Run a raw SELECT query and return (columns, rows) or ([], [])."""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(sql, params)
        rows    = cursor.fetchall()
        columns = [d[0] for d in cursor.description]
        return columns, rows
    except Exception as e:
        messagebox.showerror("Database Error", str(e))
        return [], []
    finally:
        if conn:
            conn.close()

# ─────────────────────────────────────────
#  COLORS
# ─────────────────────────────────────────
COLORS = {
    "bg":        "#1a1a2e",
    "panel":     "#16213e",
    "accent":    "#0f3460",
    "highlight": "#e94560",
    "text":      "#eaeaea",
    "muted":     "#8892a4",
    "success":   "#4ecca3",
    "entry_bg":  "#0d1b2a",
}

# ─────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────
def styled_frame(parent, **kwargs):
    return tk.Frame(parent, bg=COLORS["panel"], **kwargs)

def styled_label(parent, text, size=11, color=None, bold=False, bg=None):
    font = ("Courier New", size, "bold" if bold else "normal")
    return tk.Label(parent, text=text,
                    bg=bg or COLORS["panel"],
                    fg=color or COLORS["text"], font=font)

def styled_entry(parent, width=28):
    e = tk.Entry(parent, width=width, bg=COLORS["entry_bg"],
                 fg=COLORS["text"], insertbackground=COLORS["highlight"],
                 relief="flat", font=("Courier New", 10),
                 highlightthickness=1, highlightcolor=COLORS["highlight"],
                 highlightbackground=COLORS["accent"])
    return e

def styled_button(parent, text, command, color=None):
    return tk.Button(parent, text=text, command=command,
                     bg=color or COLORS["highlight"], fg="white",
                     font=("Courier New", 10, "bold"), relief="flat",
                     cursor="hand2", padx=12, pady=6,
                     activebackground=COLORS["accent"],
                     activeforeground="white")

def make_table(parent, columns):
    frame = tk.Frame(parent, bg=COLORS["bg"])
    frame.pack(fill="both", expand=True, padx=10, pady=10)

    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Custom.Treeview",
                    background=COLORS["entry_bg"],
                    foreground=COLORS["text"],
                    fieldbackground=COLORS["entry_bg"],
                    rowheight=26,
                    font=("Courier New", 9))
    style.configure("Custom.Treeview.Heading",
                    background=COLORS["accent"],
                    foreground=COLORS["success"],
                    font=("Courier New", 9, "bold"))
    style.map("Custom.Treeview", background=[("selected", COLORS["highlight"])])

    tree = ttk.Treeview(frame, columns=columns, show="headings",
                        style="Custom.Treeview")
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=max(100, len(col) * 11), anchor="w")

    sb_y = ttk.Scrollbar(frame, orient="vertical",   command=tree.yview)
    sb_x = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
    tree.configure(yscrollcommand=sb_y.set, xscrollcommand=sb_x.set)

    sb_y.pack(side="right",  fill="y")
    sb_x.pack(side="bottom", fill="x")
    tree.pack(fill="both", expand=True)
    return tree

def populate_table(tree, columns, rows):
    tree.delete(*tree.get_children())
    for row in rows:
        tree.insert("", "end", values=[str(v) if v is not None else "" for v in row])

# ─────────────────────────────────────────
#  PAGES — MANAGE
# ─────────────────────────────────────────

class RegisterCarPage(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=COLORS["bg"])
        styled_label(self, "Register New Car", 16, COLORS["highlight"],
                     bold=True, bg=COLORS["bg"]).pack(pady=20)

        form = styled_frame(self)
        form.pack(padx=40, pady=10, fill="x")

        fields = [("Office ID", "office_id"), ("Model", "model"),
                  ("Year",      "year"),       ("Plate ID", "plate_id")]
        self.vars = {}
        for i, (label, key) in enumerate(fields):
            styled_label(form, label).grid(row=i, column=0, sticky="w", padx=10, pady=8)
            e = styled_entry(form)
            e.grid(row=i, column=1, padx=10, pady=8)
            self.vars[key] = e

        styled_button(self, "✦  Register Car", self.submit).pack(pady=20)
        self.msg = styled_label(self, "", color=COLORS["success"], bg=COLORS["bg"])
        self.msg.pack()

    def submit(self):
        v = {k: e.get().strip() for k, e in self.vars.items()}
        if not all(v.values()):
            messagebox.showwarning("Input Error", "Please fill all fields.")
            return
        # Procedure: RegisterCar
        call_proc("RegisterCar", (v["office_id"], v["model"], v["year"], v["plate_id"]))
        self.msg.config(text="✓ Car registered successfully!")
        for e in self.vars.values():
            e.delete(0, "end")


class UpdateCarStatusPage(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=COLORS["bg"])
        styled_label(self, "Update Car Status", 16, COLORS["highlight"],
                     bold=True, bg=COLORS["bg"]).pack(pady=20)

        form = styled_frame(self)
        form.pack(padx=40, pady=10)

        styled_label(form, "Car ID").grid(row=0, column=0, sticky="w", padx=10, pady=8)
        self.car_id = styled_entry(form, width=15)
        self.car_id.grid(row=0, column=1, padx=10, pady=8)

        styled_label(form, "New Status").grid(row=1, column=0, sticky="w", padx=10, pady=8)
        self.status_var = tk.StringVar(value="active")
        combo = ttk.Combobox(form, textvariable=self.status_var,
                             values=["active", "rented", "out_of_service"],
                             state="readonly", width=20,
                             font=("Courier New", 10))
        combo.grid(row=1, column=1, padx=10, pady=8)

        styled_button(self, "✦  Update Status", self.submit).pack(pady=20)
        self.msg = styled_label(self, "", color=COLORS["success"], bg=COLORS["bg"])
        self.msg.pack()

    def submit(self):
        car_id = self.car_id.get().strip()
        status = self.status_var.get()
        if not car_id:
            messagebox.showwarning("Input Error", "Enter a Car ID.")
            return
        # Procedure: UpdateCarStatus
        cols, rows = call_proc("UpdateCarStatus", (car_id, status))
        if cols is not None:
            self.msg.config(text=f"✓ Car {car_id} status updated to '{status}'", fg=COLORS["success"])
        else:
            self.msg.config(text="✗ Update failed.", fg=COLORS["highlight"])


class RegisterCustomerPage(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=COLORS["bg"])
        styled_label(self, "Register New Customer", 16, COLORS["highlight"],
                     bold=True, bg=COLORS["bg"]).pack(pady=20)

        form = styled_frame(self)
        form.pack(padx=40, pady=10, fill="x")

        fields = [("Full Name", "name"), ("Phone",   "phone"),
                  ("Email",     "email"), ("Address", "address")]
        self.vars = {}
        for i, (label, key) in enumerate(fields):
            styled_label(form, label).grid(row=i, column=0, sticky="w", padx=10, pady=8)
            e = styled_entry(form)
            e.grid(row=i, column=1, padx=10, pady=8)
            self.vars[key] = e

        styled_button(self, "✦  Register Customer", self.submit).pack(pady=20)
        self.msg = styled_label(self, "", color=COLORS["success"], bg=COLORS["bg"])
        self.msg.pack()

    def submit(self):
        v = {k: e.get().strip() for k, e in self.vars.items()}
        if not v["name"] or not v["email"]:
            messagebox.showwarning("Input Error", "Name and Email are required.")
            return
        # Procedure: RegisterCustomer
        call_proc("RegisterCustomer", (v["name"], v["phone"], v["email"], v["address"]))
        self.msg.config(text="✓ Customer registered successfully!")
        for e in self.vars.values():
            e.delete(0, "end")


class MakeReservationPage(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=COLORS["bg"])
        styled_label(self, "Make a Reservation", 16, COLORS["highlight"],
                     bold=True, bg=COLORS["bg"]).pack(pady=20)

        form = styled_frame(self)
        form.pack(padx=40, pady=10, fill="x")

        fields = [("Car ID",                  "car_id"),
                  ("Customer ID",             "customer_id"),
                  ("Start Date (YYYY-MM-DD)", "start_date"),
                  ("End Date   (YYYY-MM-DD)", "end_date")]
        self.vars = {}
        for i, (label, key) in enumerate(fields):
            styled_label(form, label).grid(row=i, column=0, sticky="w", padx=10, pady=8)
            e = styled_entry(form)
            e.grid(row=i, column=1, padx=10, pady=8)
            self.vars[key] = e

        styled_button(self, "✦  Reserve Car", self.submit).pack(pady=20)
        self.msg = styled_label(self, "", color=COLORS["success"], bg=COLORS["bg"])
        self.msg.pack()

    def submit(self):
        v = {k: e.get().strip() for k, e in self.vars.items()}
        if not all(v.values()):
            messagebox.showwarning("Input Error", "Please fill all fields.")
            return
        # Procedure: MakeReservation
        cols, rows = call_proc("MakeReservation",
                  (v["car_id"], v["customer_id"], v["start_date"], v["end_date"]))
        if cols is not None:  # None means an error popup was already shown
            self.msg.config(text="✓ Reservation made successfully!", fg=COLORS["success"])
            for e in self.vars.values():
                e.delete(0, "end")
        else:
            self.msg.config(text="✗ Reservation failed.", fg=COLORS["highlight"])


class PickupReturnPage(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=COLORS["bg"])
        styled_label(self, "Pick Up / Return Car", 16, COLORS["highlight"],
                     bold=True, bg=COLORS["bg"]).pack(pady=20)

        form = styled_frame(self)
        form.pack(padx=40, pady=10)

        styled_label(form, "Reservation ID").grid(row=0, column=0, sticky="w", padx=10, pady=8)
        self.res_id = styled_entry(form, width=15)
        self.res_id.grid(row=0, column=1, padx=10, pady=8)

        btn_frame = tk.Frame(self, bg=COLORS["bg"])
        btn_frame.pack(pady=20)
        styled_button(btn_frame, "✦  Pick Up", self.pickup,
                      COLORS["success"]).pack(side="left", padx=10)
        styled_button(btn_frame, "✦  Return",  self.ret,
                      COLORS["highlight"]).pack(side="left", padx=10)

        self.msg = styled_label(self, "", color=COLORS["success"], bg=COLORS["bg"])
        self.msg.pack()

    def pickup(self):
        rid = self.res_id.get().strip()
        if not rid:
            messagebox.showwarning("Input Error", "Enter a Reservation ID.")
            return
        # Procedure: PickUpCar
        call_proc("PickUpCar", (rid,))
        self.msg.config(text=f"✓ Reservation {rid} marked as picked up.")

    def ret(self):
        rid = self.res_id.get().strip()
        if not rid:
            messagebox.showwarning("Input Error", "Enter a Reservation ID.")
            return
        # Procedure: ReturnCar
        call_proc("ReturnCar", (rid,))
        self.msg.config(text=f"✓ Reservation {rid} marked as returned.")


class MakePaymentPage(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=COLORS["bg"])
        styled_label(self, "Make a Payment", 16, COLORS["highlight"],
                     bold=True, bg=COLORS["bg"]).pack(pady=20)

        form = styled_frame(self)
        form.pack(padx=40, pady=10, fill="x")

        styled_label(form, "Reservation ID").grid(row=0, column=0, sticky="w", padx=10, pady=8)
        self.res_id = styled_entry(form, width=20)
        self.res_id.grid(row=0, column=1, padx=10, pady=8)

        styled_label(form, "Amount").grid(row=1, column=0, sticky="w", padx=10, pady=8)
        self.amount = styled_entry(form, width=20)
        self.amount.grid(row=1, column=1, padx=10, pady=8)

        styled_label(form, "Payment Date (YYYY-MM-DD)").grid(row=2, column=0, sticky="w", padx=10, pady=8)
        self.date = styled_entry(form, width=20)
        self.date.grid(row=2, column=1, padx=10, pady=8)

        styled_label(form, "Method").grid(row=3, column=0, sticky="w", padx=10, pady=8)
        self.method_var = tk.StringVar(value="cash")
        combo = ttk.Combobox(form, textvariable=self.method_var,
                             values=["cash", "credit_card", "debit_card", "online"],
                             state="readonly", width=20,
                             font=("Courier New", 10))
        combo.grid(row=3, column=1, padx=10, pady=8)

        styled_button(self, "✦  Submit Payment", self.submit).pack(pady=20)
        self.msg = styled_label(self, "", color=COLORS["success"], bg=COLORS["bg"])
        self.msg.pack()

    def submit(self):
        rid    = self.res_id.get().strip()
        amount = self.amount.get().strip()
        date   = self.date.get().strip()
        method = self.method_var.get()
        if not all([rid, amount, date]):
            messagebox.showwarning("Input Error", "Please fill all fields.")
            return
        # Procedure: MakePayment
        cols, rows = call_proc("MakePayment", (rid, amount, date, method))
        if cols is not None:
            self.msg.config(text="✓ Payment recorded successfully!", fg=COLORS["success"])
            self.res_id.delete(0, "end")
            self.amount.delete(0, "end")
            self.date.delete(0, "end")
        else:
            self.msg.config(text="✗ Payment failed.", fg=COLORS["highlight"])


class SearchCarsPage(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=COLORS["bg"])
        styled_label(self, "Search Available Cars", 16, COLORS["highlight"],
                     bold=True, bg=COLORS["bg"]).pack(pady=20)

        form = styled_frame(self)
        form.pack(padx=40, pady=10, fill="x")

        styled_label(form, "Model (optional)").grid(row=0, column=0, sticky="w", padx=10, pady=6)
        self.model = styled_entry(form, width=20)
        self.model.grid(row=0, column=1, padx=10, pady=6)

        styled_label(form, "Year  (optional)").grid(row=1, column=0, sticky="w", padx=10, pady=6)
        self.year = styled_entry(form, width=20)
        self.year.grid(row=1, column=1, padx=10, pady=6)

        styled_label(form, "Office ID (optional)").grid(row=2, column=0, sticky="w", padx=10, pady=6)
        self.office = styled_entry(form, width=20)
        self.office.grid(row=2, column=1, padx=10, pady=6)

        styled_button(self, "✦  Search", self.search).pack(pady=15)

        cols = ("car_id", "model", "year", "plate_id", "status", "office")
        self.tree = make_table(self, cols)

    def search(self):
        # Empty string → None so SQL receives NULL correctly
        model  = self.model.get().strip()  or None
        year   = self.year.get().strip()   or None
        office = self.office.get().strip() or None
        # Procedure: SearchCars
        cols, rows = call_proc("SearchCars", (model, year, office))
        if cols:
            populate_table(self.tree, cols, rows)


# ─────────────────────────────────────────
#  PAGES — VIEW ALL
# ─────────────────────────────────────────

class ViewAllCarsPage(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=COLORS["bg"])
        header = tk.Frame(self, bg=COLORS["bg"])
        header.pack(fill="x", pady=(20, 5))

        styled_label(header, "All Cars", 16, COLORS["highlight"],
                     bold=True, bg=COLORS["bg"]).pack(side="left", padx=20)
        styled_button(header, "⟳  Refresh", self.load,
                      COLORS["accent"]).pack(side="right", padx=20)

        cols = ("car_id", "model", "year", "plate_id", "status", "office_location")
        self.tree = make_table(self, cols)
        self.load()

    def load(self):
        sql = """
            SELECT
                ca.car_id,
                ca.model,
                ca.year,
                ca.plate_id,
                ca.status,
                o.location AS office_location
            FROM Car ca
            JOIN Office o ON ca.office_id = o.office_id
            ORDER BY ca.car_id
        """
        cols, rows = run_query(sql)
        if cols:
            populate_table(self.tree, cols, rows)


class ViewAllCustomersPage(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=COLORS["bg"])
        header = tk.Frame(self, bg=COLORS["bg"])
        header.pack(fill="x", pady=(20, 5))

        styled_label(header, "All Customers", 16, COLORS["highlight"],
                     bold=True, bg=COLORS["bg"]).pack(side="left", padx=20)
        styled_button(header, "⟳  Refresh", self.load,
                      COLORS["accent"]).pack(side="right", padx=20)

        cols = ("customer_id", "name", "phone", "email", "address")
        self.tree = make_table(self, cols)
        self.load()

    def load(self):
        sql = """
            SELECT customer_id, name, phone, email, address
            FROM Customer
            ORDER BY customer_id
        """
        cols, rows = run_query(sql)
        if cols:
            populate_table(self.tree, cols, rows)


class ViewAllReservationsPage(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=COLORS["bg"])
        header = tk.Frame(self, bg=COLORS["bg"])
        header.pack(fill="x", pady=(20, 5))

        styled_label(header, "All Reservations", 16, COLORS["highlight"],
                     bold=True, bg=COLORS["bg"]).pack(side="left", padx=20)
        styled_button(header, "⟳  Refresh", self.load,
                      COLORS["accent"]).pack(side="right", padx=20)

        cols = ("reservation_id", "start_date", "end_date", "status",
                "customer_name", "phone", "car_model", "plate_id", "office_location")
        self.tree = make_table(self, cols)
        self.load()

    def load(self):
        sql = """
            SELECT
                r.reservation_id,
                r.start_date,
                r.end_date,
                r.status,
                c.name        AS customer_name,
                c.phone,
                ca.model      AS car_model,
                ca.plate_id,
                o.location    AS office_location
            FROM Reservation r
            JOIN Customer c  ON r.customer_id = c.customer_id
            JOIN Car      ca ON r.car_id      = ca.car_id
            JOIN Office   o  ON ca.office_id  = o.office_id
            ORDER BY r.reservation_id
        """
        cols, rows = run_query(sql)
        if cols:
            populate_table(self.tree, cols, rows)


class ViewAllOfficesPage(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=COLORS["bg"])
        header = tk.Frame(self, bg=COLORS["bg"])
        header.pack(fill="x", pady=(20, 5))

        styled_label(header, "All Offices", 16, COLORS["highlight"],
                     bold=True, bg=COLORS["bg"]).pack(side="left", padx=20)
        styled_button(header, "⟳  Refresh", self.load,
                      COLORS["accent"]).pack(side="right", padx=20)

        cols = ("office_id", "location", "contact_info")
        self.tree = make_table(self, cols)
        self.load()

    def load(self):
        sql = """
            SELECT office_id, location, contact_info
            FROM Office
            ORDER BY office_id
        """
        cols, rows = run_query(sql)
        if cols:
            populate_table(self.tree, cols, rows)


class ViewAllPaymentsPage(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=COLORS["bg"])
        header = tk.Frame(self, bg=COLORS["bg"])
        header.pack(fill="x", pady=(20, 5))

        styled_label(header, "All Payments", 16, COLORS["highlight"],
                     bold=True, bg=COLORS["bg"]).pack(side="left", padx=20)
        styled_button(header, "⟳  Refresh", self.load,
                      COLORS["accent"]).pack(side="right", padx=20)

        cols = ("payment_id", "reservation_id", "customer_name",
                "car_model", "plate_id", "amount", "payment_date", "method")
        self.tree = make_table(self, cols)
        self.load()

    def load(self):
        sql = """
            SELECT
                p.payment_id,
                p.reservation_id,
                c.name          AS customer_name,
                ca.model        AS car_model,
                ca.plate_id,
                p.amount,
                p.payment_date,
                p.method
            FROM Payment p
            JOIN Reservation r ON p.reservation_id = r.reservation_id
            JOIN Customer    c ON r.customer_id    = c.customer_id
            JOIN Car        ca ON r.car_id         = ca.car_id
            ORDER BY p.payment_id
        """
        cols, rows = run_query(sql)
        if cols:
            populate_table(self.tree, cols, rows)


# ─────────────────────────────────────────
#  PAGES — REPORTS
# ─────────────────────────────────────────

class ReportReservationsPage(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=COLORS["bg"])
        styled_label(self, "Report: Reservations by Period", 16, COLORS["highlight"],
                     bold=True, bg=COLORS["bg"]).pack(pady=20)

        form = styled_frame(self)
        form.pack(padx=40, pady=5, fill="x")

        styled_label(form, "Start Date (YYYY-MM-DD)").grid(row=0, column=0, sticky="w", padx=10, pady=6)
        self.start = styled_entry(form, width=18)
        self.start.grid(row=0, column=1, padx=10, pady=6)

        styled_label(form, "End Date   (YYYY-MM-DD)").grid(row=1, column=0, sticky="w", padx=10, pady=6)
        self.end = styled_entry(form, width=18)
        self.end.grid(row=1, column=1, padx=10, pady=6)

        styled_button(self, "✦  Generate Report", self.generate).pack(pady=12)

        cols = ("reservation_id", "start_date", "end_date", "reservation_status",
                "customer_name", "phone", "email", "car_model",
                "plate_id", "year", "office_location")
        self.tree = make_table(self, cols)

    def generate(self):
        s, e = self.start.get().strip(), self.end.get().strip()
        if not s or not e:
            messagebox.showwarning("Input Error", "Enter both dates.")
            return
        # Procedure: ReportReservationsByPeriod
        cols, rows = call_proc("ReportReservationsByPeriod", (s, e))
        if cols:
            populate_table(self.tree, cols, rows)


class ReportCarStatusPage(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=COLORS["bg"])
        styled_label(self, "Report: Car Status on a Day", 16, COLORS["highlight"],
                     bold=True, bg=COLORS["bg"]).pack(pady=20)

        form = styled_frame(self)
        form.pack(padx=40, pady=5)

        styled_label(form, "Date (YYYY-MM-DD)").grid(row=0, column=0, sticky="w", padx=10, pady=6)
        self.day = styled_entry(form, width=18)
        self.day.grid(row=0, column=1, padx=10, pady=6)

        styled_button(self, "✦  Generate Report", self.generate).pack(pady=12)

        cols = ("car_id", "model", "plate_id", "year", "office", "status_on_day")
        self.tree = make_table(self, cols)

    def generate(self):
        day = self.day.get().strip()
        if not day:
            messagebox.showwarning("Input Error", "Enter a date.")
            return
        # Procedure: ReportCarStatusOnDay
        cols, rows = call_proc("ReportCarStatusOnDay", (day,))
        if cols:
            populate_table(self.tree, cols, rows)


class ReportCustomerPage(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=COLORS["bg"])
        styled_label(self, "Report: Customer Reservations", 16, COLORS["highlight"],
                     bold=True, bg=COLORS["bg"]).pack(pady=20)

        form = styled_frame(self)
        form.pack(padx=40, pady=5)

        styled_label(form, "Customer ID").grid(row=0, column=0, sticky="w", padx=10, pady=6)
        self.cid = styled_entry(form, width=18)
        self.cid.grid(row=0, column=1, padx=10, pady=6)

        styled_button(self, "✦  Generate Report", self.generate).pack(pady=12)

        cols = ("reservation_id", "start_date", "end_date", "reservation_status",
                "customer_id", "customer_name", "phone", "email",
                "car_model", "plate_id")
        self.tree = make_table(self, cols)

    def generate(self):
        cid = self.cid.get().strip()
        if not cid:
            messagebox.showwarning("Input Error", "Enter a Customer ID.")
            return
        # Procedure: ReportCustomerReservations
        cols, rows = call_proc("ReportCustomerReservations", (cid,))
        if cols:
            populate_table(self.tree, cols, rows)


class ReportPaymentsPage(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=COLORS["bg"])
        styled_label(self, "Report: Daily Payments", 16, COLORS["highlight"],
                     bold=True, bg=COLORS["bg"]).pack(pady=20)

        form = styled_frame(self)
        form.pack(padx=40, pady=5)

        styled_label(form, "Start Date (YYYY-MM-DD)").grid(row=0, column=0, sticky="w", padx=10, pady=6)
        self.start = styled_entry(form, width=18)
        self.start.grid(row=0, column=1, padx=10, pady=6)

        styled_label(form, "End Date   (YYYY-MM-DD)").grid(row=1, column=0, sticky="w", padx=10, pady=6)
        self.end = styled_entry(form, width=18)
        self.end.grid(row=1, column=1, padx=10, pady=6)

        styled_button(self, "✦  Generate Report", self.generate).pack(pady=12)

        cols = ("payment_date", "total_daily_revenue",
                "number_of_payments", "payment_methods")
        self.tree = make_table(self, cols)

    def generate(self):
        s, e = self.start.get().strip(), self.end.get().strip()
        if not s or not e:
            messagebox.showwarning("Input Error", "Enter both dates.")
            return
        # Procedure: ReportDailyPayments
        cols, rows = call_proc("ReportDailyPayments", (s, e))
        if cols:
            populate_table(self.tree, cols, rows)


# ─────────────────────────────────────────
#  MAIN APP
# ─────────────────────────────────────────

class CarRentalApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Car Rental System — ANU 2026")
        self.geometry("1100x700")
        self.configure(bg=COLORS["bg"])
        self.resizable(True, True)

        self._build_sidebar()
        self._build_content()
        self.show_page("register_car")

    def _build_sidebar(self):
        # Outer container holds the logo + scrollable nav area
        sidebar_outer = tk.Frame(self, bg=COLORS["panel"], width=220)
        sidebar_outer.pack(side="left", fill="y")
        sidebar_outer.pack_propagate(False)

        # Logo / title — always visible at top
        tk.Label(sidebar_outer, text="🚗", font=("Arial", 32),
                 bg=COLORS["panel"], fg=COLORS["highlight"]).pack(pady=(20, 4))
        tk.Label(sidebar_outer, text="Car Rental\nSystem",
                 font=("Courier New", 12, "bold"),
                 bg=COLORS["panel"], fg=COLORS["text"],
                 justify="center").pack(pady=(0, 12))
        tk.Frame(sidebar_outer, bg=COLORS["accent"], height=1).pack(fill="x", padx=20, pady=(0, 4))

        # Scrollable canvas for nav buttons
        canvas = tk.Canvas(sidebar_outer, bg=COLORS["panel"],
                           highlightthickness=0, bd=0)
        scrollbar = ttk.Scrollbar(sidebar_outer, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        # Inner frame inside canvas
        nav_frame = tk.Frame(canvas, bg=COLORS["panel"])
        nav_window = canvas.create_window((0, 0), window=nav_frame, anchor="nw")

        def on_frame_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        def on_canvas_configure(event):
            canvas.itemconfig(nav_window, width=event.width)

        nav_frame.bind("<Configure>", on_frame_configure)
        canvas.bind("<Configure>", on_canvas_configure)

        # Mouse-wheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        sections = [
            ("── MANAGE ──",         None),
            ("  Register Car",        "register_car"),
            ("  Update Car Status",   "update_status"),
            ("  Register Customer",   "register_customer"),
            ("  Make Reservation",    "make_reservation"),
            ("  Pick Up / Return",    "pickup_return"),
            ("  Make Payment",        "make_payment"),
            ("  Search Cars",         "search_cars"),
            ("── VIEW ALL ──",        None),
            ("  All Cars",            "view_all_cars"),
            ("  All Customers",       "view_all_customers"),
            ("  All Reservations",    "view_all_reservations"),
            ("  All Offices",         "view_all_offices"),
            ("  All Payments",        "view_all_payments"),
            ("── REPORTS ──",         None),
            ("  Reservations",        "report_reservations"),
            ("  Car Status on Day",   "report_car_status"),
            ("  Customer History",    "report_customer"),
            ("  Daily Payments",      "report_payments"),
        ]

        self.nav_buttons = {}
        for label, page_key in sections:
            if page_key is None:
                tk.Label(nav_frame, text=label,
                         font=("Courier New", 8, "bold"),
                         bg=COLORS["panel"], fg=COLORS["muted"],
                         anchor="w").pack(fill="x", padx=15, pady=(14, 2))
            else:
                btn = tk.Button(nav_frame, text=label, anchor="w",
                                font=("Courier New", 10),
                                bg=COLORS["panel"], fg=COLORS["text"],
                                activebackground=COLORS["highlight"],
                                activeforeground="white",
                                relief="flat", cursor="hand2",
                                padx=15, pady=7,
                                command=lambda k=page_key: self.show_page(k))
                btn.pack(fill="x", padx=8, pady=1)
                self.nav_buttons[page_key] = btn

    def _build_content(self):
        self.content = tk.Frame(self, bg=COLORS["bg"])
        self.content.pack(side="right", fill="both", expand=True)

        self.pages = {
            # Manage
            "register_car":         RegisterCarPage(self.content),
            "update_status":        UpdateCarStatusPage(self.content),
            "register_customer":    RegisterCustomerPage(self.content),
            "make_reservation":     MakeReservationPage(self.content),
            "pickup_return":        PickupReturnPage(self.content),
            "make_payment":         MakePaymentPage(self.content),
            "search_cars":          SearchCarsPage(self.content),
            # View All
            "view_all_cars":        ViewAllCarsPage(self.content),
            "view_all_customers":   ViewAllCustomersPage(self.content),
            "view_all_reservations":ViewAllReservationsPage(self.content),
            "view_all_offices":     ViewAllOfficesPage(self.content),
            "view_all_payments":    ViewAllPaymentsPage(self.content),
            # Reports
            "report_reservations":  ReportReservationsPage(self.content),
            "report_car_status":    ReportCarStatusPage(self.content),
            "report_customer":      ReportCustomerPage(self.content),
            "report_payments":      ReportPaymentsPage(self.content),
        }
        for page in self.pages.values():
            page.place(relwidth=1, relheight=1)

    def show_page(self, key):
        # Refresh view-all pages every time they're opened
        if key in ("view_all_cars", "view_all_customers", "view_all_reservations", "view_all_offices", "view_all_payments"):
            self.pages[key].load()

        for k, btn in self.nav_buttons.items():
            btn.config(bg=COLORS["highlight"] if k == key else COLORS["panel"],
                       fg="white"             if k == key else COLORS["text"])
        self.pages[key].lift()


if __name__ == "__main__":
    app = CarRentalApp()
    app.mainloop()